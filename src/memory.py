"""Conversational and Semantic Memory Manager using ChromaDB and persistent User Profile."""

import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings

from src.config import CHROMA_PERSIST_DIR, USER_PROFILES_FILE
from src.catalog import get_all_products


class MemoryManager:
    """Manages conversational vector memory in ChromaDB and structured user preferences."""

    def __init__(self, persist_dir: Optional[str] = None):
        self.persist_dir = str(persist_dir or CHROMA_PERSIST_DIR)
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        
        # Collection for episodic conversation turns and learned insights
        self.conversation_col = self.client.get_or_create_collection(
            name="shopping_conversation_memory",
            metadata={"description": "Stores user messages, preferences, and assistant suggestions for episodic recall"}
        )
        
        # Collection for semantic product vector search
        self.product_col = self.client.get_or_create_collection(
            name="shopping_product_catalog",
            metadata={"description": "Stores indexed products and review summaries for vector search"}
        )

        self._profile_file = USER_PROFILES_FILE
        self._load_or_init_profile()
        self._ensure_products_indexed()

    def _load_or_init_profile(self):
        """Load user profile from JSON or initialize default structure."""
        if self._profile_file.exists():
            try:
                with open(self._profile_file, "r", encoding="utf-8") as f:
                    self.profile = json.load(f)
                    return
            except Exception:
                pass
        
        self.profile = {
            "user_id": "default_shopper",
            "preferred_brands": [],
            "disliked_brands": [],
            "favorite_categories": [],
            "budget_tier": "Flexible",
            "max_budget": None,
            "sizes": {},
            "lifestyle_notes": [],
            "special_requirements": [],
            "last_active": datetime.now().isoformat()
        }
        self.save_profile()

    def save_profile(self):
        """Persist structured user profile to disk."""
        self.profile["last_active"] = datetime.now().isoformat()
        try:
            with open(self._profile_file, "w", encoding="utf-8") as f:
                json.dump(self.profile, f, indent=2)
        except Exception as e:
            print(f"Error saving profile: {e}")

    def _ensure_products_indexed(self):
        """Index all products into ChromaDB if not already present."""
        existing_count = self.product_col.count()
        products = get_all_products()
        if existing_count < len(products):
            documents = []
            ids = []
            metadatas = []
            for p in products:
                # Build rich textual representation for vector indexing
                specs_str = "; ".join([f"{k}: {v}" for k, v in p.get("specs", {}).items()])
                reviews_summary = " ".join([f"{r.get('pros', '')} {r.get('text', '')}" for r in p.get("reviews", [])])
                doc = (
                    f"Product: {p['title']} by {p['brand']}.\n"
                    f"Category: {p['category']}.\n"
                    f"Price: ${p['price']} (Original: ${p.get('original_price', p['price'])}).\n"
                    f"Rating: {p['rating']} stars ({p['review_count']} reviews).\n"
                    f"Description: {p['description']}\n"
                    f"Specs: {specs_str}.\n"
                    f"Tags: {', '.join(p['tags'])}.\n"
                    f"Customer feedback highlights: {reviews_summary}"
                )
                documents.append(doc)
                ids.append(p["id"])
                metadatas.append({
                    "id": p["id"],
                    "title": p["title"],
                    "brand": p["brand"],
                    "category": p["category"],
                    "price": float(p["price"]),
                    "rating": float(p["rating"])
                })
            
            self.product_col.upsert(
                documents=documents,
                ids=ids,
                metadatas=metadatas
            )

    def search_products_semantically(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Vector similarity search against the indexed product catalog in ChromaDB."""
        try:
            results = self.product_col.query(
                query_texts=[query],
                n_results=n_results
            )
            matched_ids = results.get("ids", [[]])[0]
            matched_products = []
            for pid in matched_ids:
                from src.catalog import get_product_by_id
                prod = get_product_by_id(pid)
                if prod:
                    matched_products.append(prod)
            return matched_products
        except Exception as e:
            print(f"Semantic search error: {e}")
            from src.catalog import search_products
            return search_products(query=query, limit=n_results)

    def record_interaction(self, role: str, content: str, topic: str = "general", metadata: Optional[Dict[str, Any]] = None):
        """Store a conversation turn or user intent in ChromaDB episodic memory."""
        doc_id = f"mem_{uuid.uuid4().hex[:12]}"
        meta = {
            "role": role,
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
        }
        if metadata:
            for k, v in metadata.items():
                if isinstance(v, (str, int, float, bool)):
                    meta[k] = v
                else:
                    meta[k] = str(v)

        try:
            self.conversation_col.add(
                documents=[f"[{role.upper()}]: {content}"],
                ids=[doc_id],
                metadatas=[meta]
            )
        except Exception as e:
            print(f"Error adding to Chroma memory: {e}")

        # Also auto-extract potential preferences if user spoke
        if role.lower() == "user":
            self.extract_and_update_preferences(content)

    def recall_relevant_memories(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Retrieve relevant past conversation turns and user statements from ChromaDB."""
        if self.conversation_col.count() == 0:
            return []
        try:
            res = self.conversation_col.query(
                query_texts=[query],
                n_results=min(n_results, self.conversation_col.count())
            )
            docs = res.get("documents", [[]])[0]
            metas = res.get("metadatas", [[]])[0]
            memories = []
            for d, m in zip(docs, metas):
                memories.append({
                    "content": d,
                    "metadata": m
                })
            return memories
        except Exception as e:
            print(f"Chroma memory recall error: {e}")
            return []

    def get_user_profile(self) -> Dict[str, Any]:
        """Return the current user profile preferences."""
        return self.profile

    def update_preference(self, key: str, value: Any):
        """Directly update a preference key in user profile."""
        if key in ["preferred_brands", "disliked_brands", "favorite_categories", "lifestyle_notes", "special_requirements"]:
            if isinstance(value, list):
                self.profile[key] = list(set(self.profile.get(key, []) + value))
            elif isinstance(value, str):
                if value not in self.profile.get(key, []):
                    self.profile.setdefault(key, []).append(value)
        elif key == "sizes":
            if isinstance(value, dict):
                self.profile.setdefault("sizes", {}).update(value)
        else:
            self.profile[key] = value
        self.save_profile()

    def remove_preference_item(self, key: str, item: str):
        """Remove a specific item from a preference list."""
        if key in self.profile and isinstance(self.profile[key], list):
            self.profile[key] = [x for x in self.profile[key] if x.lower() != item.lower()]
            self.save_profile()

    def clear_all_memories(self):
        """Reset conversation memory in Chroma and user profile."""
        try:
            self.client.delete_collection("shopping_conversation_memory")
            self.conversation_col = self.client.get_or_create_collection(
                name="shopping_conversation_memory"
            )
        except Exception:
            pass
        self._load_or_init_profile()
        self.profile = {
            "user_id": "default_shopper",
            "preferred_brands": [],
            "disliked_brands": [],
            "favorite_categories": [],
            "budget_tier": "Flexible",
            "max_budget": None,
            "sizes": {},
            "lifestyle_notes": [],
            "special_requirements": [],
            "last_active": datetime.now().isoformat()
        }
        self.save_profile()

    def extract_and_update_preferences(self, user_text: str):
        """Parse user input for explicit preferences like budget, brands, or sizes."""
        text_lower = user_text.lower()
        import re

        # Detect shoe size
        shoe_match = re.search(r'\b(?:shoe\s*size|size)\s*(?:is|of|:)?\s*([us\d\.\s]+)\b', text_lower)
        if shoe_match and any(c.isdigit() for c in shoe_match.group(1)):
            size_val = shoe_match.group(1).strip()
            self.update_preference("sizes", {"shoes": size_val.upper()})

        # Detect budget constraint
        budget_match = re.search(r'(?:budget\s*(?:is|of)?|under|less\s*than|below|max)\s*\$?(\d+(?:\.\d+)?)', text_lower)
        if budget_match:
            try:
                b_val = float(budget_match.group(1))
                if b_val > 5:  # Avoid matching arbitrary small numbers
                    self.update_preference("max_budget", b_val)
                    if b_val < 150:
                        self.update_preference("budget_tier", "Budget-conscious")
                    elif b_val < 600:
                        self.update_preference("budget_tier", "Mid-range")
                    else:
                        self.update_preference("budget_tier", "Premium")
            except Exception:
                pass

        # Detect brand affinities
        from src.catalog import get_brands
        for brand in get_brands():
            b_lower = brand.lower()
            if f"love {b_lower}" in text_lower or f"prefer {b_lower}" in text_lower or f"fan of {b_lower}" in text_lower or f"like {b_lower}" in text_lower:
                self.update_preference("preferred_brands", brand)
            if f"hate {b_lower}" in text_lower or f"don't like {b_lower}" in text_lower or f"avoid {b_lower}" in text_lower or f"no {b_lower}" in text_lower:
                self.update_preference("disliked_brands", brand)

        # Detect lifestyle / special requirements
        if "travel" in text_lower or "flight" in text_lower or "airplane" in text_lower:
            self.update_preference("lifestyle_notes", "Frequent traveler / Air commute")
        if "running" in text_lower or "marathon" in text_lower or "jogging" in text_lower:
            self.update_preference("lifestyle_notes", "Runner / Active fitness enthusiast")
        if "vegan" in text_lower or "cruelty free" in text_lower:
            self.update_preference("special_requirements", "Prefers vegan / cruelty-free materials")
        if "eco" in text_lower or "sustainable" in text_lower or "recycled" in text_lower:
            self.update_preference("special_requirements", "Prefers sustainable / recycled products")
        if "small apartment" in text_lower or "compact" in text_lower:
            self.update_preference("lifestyle_notes", "Compact living space / Prefers space-saving items")

    def format_memory_summary_for_prompt(self) -> str:
        """Format persistent user profile and relevant memories for LLM prompt injection."""
        p = self.profile
        lines = ["=== USER MEMORY & PREFERENCES PROFILE ==="]
        if p.get("preferred_brands"):
            lines.append(f"- Preferred Brands: {', '.join(p['preferred_brands'])}")
        if p.get("disliked_brands"):
            lines.append(f"- Disliked Brands to Avoid: {', '.join(p['disliked_brands'])}")
        if p.get("max_budget"):
            lines.append(f"- Hard Budget Ceiling: ${p['max_budget']:.2f}")
        if p.get("budget_tier") and p["budget_tier"] != "Flexible":
            lines.append(f"- Budget Mindset: {p['budget_tier']}")
        if p.get("sizes"):
            sizes_str = ", ".join([f"{k}: {v}" for k, v in p["sizes"].items()])
            lines.append(f"- Known Sizing: {sizes_str}")
        if p.get("lifestyle_notes"):
            lines.append(f"- Lifestyle Attributes: {'; '.join(p['lifestyle_notes'])}")
        if p.get("special_requirements"):
            lines.append(f"- Special Needs/Values: {'; '.join(p['special_requirements'])}")
        
        if len(lines) == 1:
            return "No specific long-term user preferences recorded yet."
        return "\n".join(lines)


# Singleton memory instance
_memory_instance: Optional[MemoryManager] = None

def get_memory_manager() -> MemoryManager:
    """Get or create singleton memory manager."""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = MemoryManager()
    return _memory_instance
