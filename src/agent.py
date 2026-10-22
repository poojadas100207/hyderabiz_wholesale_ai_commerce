"""Autonomous E-Commerce Shopping Concierge Agent implementation using LangChain and Gemini API."""

import re
from typing import List, Dict, Any, Optional
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from src.config import get_api_key, DEFAULT_MODEL, FALLBACK_MODELS
from src.tools import ALL_TOOLS
from src.memory import get_memory_manager
from src.catalog import get_all_products, get_product_by_id, search_products
from src.tracker import get_price_tracker
from src.cart import get_shopping_cart

SYSTEM_PROMPT_TEMPLATE = """You are Aura, an elite Autonomous E-Commerce Shopping Concierge Agent.
Your mission is to provide an ultra-personalized, insightful, and frictionless shopping experience.

You are equipped with:
- Conversational Vector Memory: Recalls user history, past shopping interests, and habits from ChromaDB.
- Long-Term User Profile: Tracks brand affinities, sizing, budget restrictions, and lifestyle requirements.
- Real-Time Product Catalog & Specs: Up-to-date specs, pricing, and stock levels.
- Customer Review Summarizer: Deep sentiment analysis identifying recurring pros, cons, and quirks.
- Price Drop Tracker: Ability to set alerts and monitor market discounts.
- Smart Cart Assistant: Adds items, estimates shipping, taxes, and applies promotional codes.

{memory_context}

{recalled_memories}

Guidelines for Interaction:
1. Empathy & Personalization: Tailor every recommendation to the user's active profile and budget.
2. Proactive Insights: If an item has recurring customer complaints (e.g. narrow toe box, short battery), highlight it honestly.
3. Budget Respect: If an item exceeds the user's budget, explicitly mention it and offer to set a Price Drop Alert!
4. Autonomous Tool Use: Call tools whenever you need product facts, review summaries, memory updates, or cart actions. Never invent product IDs or fake specifications.
5. Formatted Output: Use clean Markdown, bullet points, and highlight product IDs (e.g. `[PROD-101]`) so users can take quick action.
"""


class ShoppingConciergeAgent:
    """Autonomous Shopping Agent using LangChain and Gemini API with smart offline fallback."""

    def __init__(self, model_name: str = DEFAULT_MODEL):
        self.model_name = model_name
        self.memory = get_memory_manager()
        self.tools = ALL_TOOLS
        self.tool_map = {tool.name: tool for tool in self.tools}
        self._llm = None
        self._llm_with_tools = None

    def _init_llm(self) -> bool:
        """Initialize LangChain Gemini model if API key is present."""
        api_key = get_api_key()
        if not api_key:
            return False

        try:
            # Attempt with selected model or fallback models
            models_to_try = [self.model_name] + [m for m in FALLBACK_MODELS if m != self.model_name]
            last_err = None
            for m in models_to_try:
                try:
                    llm = ChatGoogleGenerativeAI(
                        model=m,
                        google_api_key=api_key,
                        temperature=0.3,
                        max_retries=2
                    )
                    self._llm = llm
                    self._llm_with_tools = llm.bind_tools(self.tools)
                    self.model_name = m
                    return True
                except Exception as err:
                    last_err = err
                    continue
            print(f"Warning: Failed to init Gemini model: {last_err}")
            return False
        except Exception as e:
            print(f"Error setting up Gemini LLM: {e}")
            return False

    def run(self, user_message: str, chat_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """Execute agentic workflow for the user query."""
        chat_history = chat_history or []
        agent_steps = []

        # 1. Retrieve memory & contextual background
        user_profile_summary = self.memory.format_memory_summary_for_prompt()
        semantic_memories = self.memory.recall_relevant_memories(user_message, n_results=2)
        
        recalled_str = ""
        if semantic_memories:
            recalled_str = "Relevant Episodic Context from ChromaDB:\n" + "\n".join(
                [f"• {m['content']}" for m in semantic_memories]
            )

        # 2. Check if Gemini LLM is available
        llm_ready = self._init_llm()

        if llm_ready and self._llm_with_tools:
            try:
                return self._run_gemini_agent(
                    user_message=user_message,
                    chat_history=chat_history,
                    profile_summary=user_profile_summary,
                    recalled_memories=recalled_str
                )
            except Exception as e:
                print(f"Gemini execution error (switching to fallback): {e}")
                # Fallback gracefully if rate-limited or network issue occurs
                return self._run_fallback_agent(user_message, agent_steps, fallback_reason=str(e))
        else:
            return self._run_fallback_agent(user_message, agent_steps)

    def _run_gemini_agent(
        self,
        user_message: str,
        chat_history: List[Dict[str, str]],
        profile_summary: str,
        recalled_memories: str
    ) -> Dict[str, Any]:
        """Run tool-calling autonomous loop with Gemini via LangChain."""
        agent_steps = []

        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            memory_context=profile_summary,
            recalled_memories=recalled_memories
        )

        messages = [SystemMessage(content=system_prompt)]

        # Add recent conversation turns
        for turn in chat_history[-6:]:
            role = turn.get("role", "")
            content = turn.get("content", "")
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))

        messages.append(HumanMessage(content=user_message))

        # Autonomous tool-calling loop (up to 5 reasoning hops)
        max_iterations = 5
        for step_idx in range(max_iterations):
            ai_msg = self._llm_with_tools.invoke(messages)
            messages.append(ai_msg)

            if not ai_msg.tool_calls:
                # No more tools required; agent has formulated its final response
                break

            for tool_call in ai_msg.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_call_id = tool_call["id"]

                agent_steps.append({
                    "step": step_idx + 1,
                    "tool": tool_name,
                    "input": tool_args
                })

                tool_fn = self.tool_map.get(tool_name)
                if tool_fn:
                    try:
                        tool_result = tool_fn.invoke(tool_args)
                    except Exception as err:
                        tool_result = f"Error executing {tool_name}: {err}"
                else:
                    tool_result = f"Tool '{tool_name}' not found."

                agent_steps[-1]["output"] = str(tool_result)[:300] + ("..." if len(str(tool_result)) > 300 else "")
                messages.append(ToolMessage(content=str(tool_result), tool_call_id=tool_call_id))

        final_response = messages[-1].content

        # Record turn in ChromaDB vector memory
        self.memory.record_interaction("user", user_message)
        self.memory.record_interaction("assistant", final_response)

        return {
            "response": final_response,
            "agent_steps": agent_steps,
            "mode": f"gemini ({self.model_name})"
        }

    def _run_fallback_agent(
        self,
        user_message: str,
        agent_steps: List[Dict[str, Any]],
        fallback_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Intelligent offline concierge engine executing identical LangChain tools and ChromaDB memory."""
        text_lower = user_message.lower().strip()
        response_parts = []
        memory = self.memory
        tracker = get_price_tracker()
        cart = get_shopping_cart()

        # Update memory automatically
        memory.extract_and_update_preferences(user_message)
        memory.record_interaction("user", user_message)

        # Detect Intent 1: Price Tracking / Price Alerts
        if any(w in text_lower for w in ["track price", "price drop", "alert me", "watch price", "notify if price"]):
            # Extract target price if present
            price_match = re.search(r'\$?(\d+(?:\.\d+)?)', text_lower)
            target_price = float(price_match.group(1)) if price_match else None
            
            # Find referenced product
            found_product = None
            for p in get_all_products():
                if p["id"].lower() in text_lower or any(word in text_lower for word in p["title"].lower().split() if len(word) > 4):
                    found_product = p
                    break

            if found_product and target_price:
                step_entry = {"tool": "track_price_drop_tool", "input": {"product_id": found_product["id"], "target_price": target_price}}
                tool_out = self.tool_map["track_price_drop_tool"].invoke({"product_id": found_product["id"], "target_price": target_price})
                step_entry["output"] = tool_out
                agent_steps.append(step_entry)
                response_parts.append(f"🎯 **Price Drop Alert Set!**\n\n{tool_out}\n\nCurrent Price: **${found_product['price']:.2f}** | Alert Target: **${target_price:.2f}**.")
            else:
                step_entry = {"tool": "check_price_drop_alerts_tool", "input": {}}
                tool_out = self.tool_map["check_price_drop_alerts_tool"].invoke({})
                step_entry["output"] = tool_out
                agent_steps.append(step_entry)
                response_parts.append(f"📊 **Price Drop Monitor Status:**\n\n{tool_out}")

        # Detect Intent 2: Review Summarization
        elif any(w in text_lower for w in ["review", "reviews", "sentiment", "complaint", "feedback", "what do users say"]):
            found_product = None
            for p in get_all_products():
                if p["id"].lower() in text_lower or any(word in text_lower for word in p["title"].lower().split() if len(word) > 4):
                    found_product = p
                    break

            if found_product:
                step_entry = {"tool": "summarize_reviews_tool", "input": {"product_id": found_product["id"]}}
                tool_out = self.tool_map["summarize_reviews_tool"].invoke({"product_id": found_product["id"]})
                step_entry["output"] = tool_out[:250] + "..."
                agent_steps.append(step_entry)
                response_parts.append(f"⭐ **Customer Review Intelligence for {found_product['title']}**\n\n{tool_out}")
            else:
                response_parts.append("Which product's reviews would you like me to analyze? (e.g. Sony WH-1000XM5, Dyson V12, Hoka Clifton 9, Breville Espresso).")

        # Detect Intent 3: Product Comparison
        elif "compare" in text_lower or " vs " in text_lower or "versus" in text_lower:
            matched_products = []
            for p in get_all_products():
                if p["brand"].lower() in text_lower or p["id"].lower() in text_lower or any(w in text_lower for w in p["title"].lower().split() if len(w) > 4):
                    if p not in matched_products:
                        matched_products.append(p)

            if len(matched_products) >= 2:
                p1, p2 = matched_products[0], matched_products[1]
                step_entry = {"tool": "compare_products_tool", "input": {"product_id_1": p1["id"], "product_id_2": p2["id"]}}
                tool_out = self.tool_map["compare_products_tool"].invoke({"product_id_1": p1["id"], "product_id_2": p2["id"]})
                step_entry["output"] = tool_out[:250] + "..."
                agent_steps.append(step_entry)
                response_parts.append(tool_out)
            else:
                response_parts.append("Please specify two products to compare (for example: *'Compare Sony WH-1000XM5 and Bose QC Ultra'*).")

        # Detect Intent 4: Cart Management
        elif any(w in text_lower for w in ["cart", "checkout", "add to cart", "buy", "promo", "coupon"]):
            if "add" in text_lower:
                found_p = None
                for p in get_all_products():
                    if p["id"].lower() in text_lower or any(w in text_lower for w in p["title"].lower().split() if len(w) > 4):
                        found_p = p
                        break
                if found_p:
                    step_entry = {"tool": "manage_cart_tool", "input": {"action": "add", "product_id": found_p["id"]}}
                    tool_out = self.tool_map["manage_cart_tool"].invoke({"action": "add", "product_id": found_p["id"]})
                    step_entry["output"] = tool_out
                    agent_steps.append(step_entry)
                    response_parts.append(f"🛒 **Cart Updated!**\n\n{tool_out}")
                else:
                    response_parts.append("Which item would you like to add to your cart? Please mention the product name or ID.")
            elif "promo" in text_lower or "coupon" in text_lower or "code" in text_lower:
                code_match = re.search(r'\b(welcome10|concierge20|flash15)\b', text_lower)
                code = code_match.group(1).upper() if code_match else "WELCOME10"
                step_entry = {"tool": "manage_cart_tool", "input": {"action": "apply_promo", "promo_code": code}}
                tool_out = self.tool_map["manage_cart_tool"].invoke({"action": "apply_promo", "promo_code": code})
                step_entry["output"] = tool_out
                agent_steps.append(step_entry)
                response_parts.append(tool_out)
            else:
                step_entry = {"tool": "manage_cart_tool", "input": {"action": "view"}}
                tool_out = self.tool_map["manage_cart_tool"].invoke({"action": "view"})
                step_entry["output"] = tool_out
                agent_steps.append(step_entry)
                response_parts.append(tool_out)

        # Detect Intent 5: Memory / Recall
        elif any(w in text_lower for w in ["what do you remember", "my preference", "my profile", "do you recall", "my budget", "my size"]):
            step_entry = {"tool": "recall_user_memory_tool", "input": {"query": user_message}}
            tool_out = self.tool_map["recall_user_memory_tool"].invoke({"query": user_message})
            step_entry["output"] = tool_out
            agent_steps.append(step_entry)
            
            profile = memory.get_user_profile()
            response_parts.append(f"🧠 **Conversational Memory Recall:**\n\n{memory.format_memory_summary_for_prompt()}\n\n{tool_out}")

        # Default Intent 6: Product Search & Recommendation
        else:
            # Check price filters
            max_p = None
            price_match = re.search(r'(?:under|below|less than|max)\s*\$?(\d+(?:\.\d+)?)', text_lower)
            if price_match:
                max_p = float(price_match.group(1))

            step_entry = {"tool": "search_products_tool", "input": {"query": user_message, "max_price": max_p}}
            tool_out = self.tool_map["search_products_tool"].invoke({"query": user_message, "max_price": max_p})
            step_entry["output"] = tool_out[:250] + "..."
            agent_steps.append(step_entry)

            profile = memory.get_user_profile()
            pref_note = ""
            if profile.get("preferred_brands"):
                pref_note = f"\n*(Personalized with your brand affinity for: {', '.join(profile['preferred_brands'])})*"

            response_parts.append(
                f"Here are my tailored recommendations based on your preferences:\n\n{tool_out}\n{pref_note}\n\n"
                f"💡 *Would you like me to summarize reviews, compare any two of these, track a price drop, or add an item to your cart?*"
            )

        final_response = "\n\n".join(response_parts)
        memory.record_interaction("assistant", final_response)

        mode_msg = "Offline Autonomous Concierge"
        if fallback_reason:
            mode_msg += f" (Gemini note: {fallback_reason[:60]}...)"

        return {
            "response": final_response,
            "agent_steps": agent_steps,
            "mode": mode_msg
        }
