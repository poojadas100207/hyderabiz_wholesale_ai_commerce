"""Command Line Interface (CLI) for Autonomous E-Commerce Shopping Concierge Agent."""

import sys
import os
from pathlib import Path

# Fix Windows console UTF-8 output
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.agent import ShoppingConciergeAgent
from src.tracker import get_price_tracker
from src.memory import get_memory_manager
from src.cart import get_shopping_cart
from src.config import get_api_key


def main():
    agent = ShoppingConciergeAgent()
    tracker = get_price_tracker()
    memory = get_memory_manager()
    cart = get_shopping_cart()

    api_key = get_api_key()
    mode_str = f"Gemini API ({agent.model_name})" if api_key else "Offline Autonomous Concierge"

    print("=" * 70)
    print("      AURA - AUTONOMOUS E-COMMERCE SHOPPING CONCIERGE AGENT")
    print(f"      Mode: {mode_str}")
    print("=" * 70)
    print("Commands: 'quit', 'cart', 'alerts', 'memory', 'simulate <prod_id> <pct>', 'clear'")
    print("-" * 70)

    history = []

    while True:
        try:
            user_input = input("\nYou > ").strip()
            if not user_input:
                continue

            cmd = user_input.lower()
            if cmd in ["quit", "exit", "q"]:
                print("\nThank you for shopping with Aura! Goodbye.")
                break

            elif cmd == "cart":
                s = cart.get_summary()
                print("\n--- SHOPPING CART ---")
                if not s["items"]:
                    print("Your cart is currently empty.")
                else:
                    for it in s["items"]:
                        print(f"• {it['quantity']}x {it['title']} - ${it['unit_price']:.2f} (${it['item_total']:.2f})")
                    print(f"Subtotal: ${s['subtotal']:.2f}")
                    if s.get("promo_code"):
                        print(f"Promo ({s['promo_code']}): -${s['discount_amount']:.2f}")
                    print(f"Shipping: ${s['shipping']:.2f} | Tax: ${s['tax']:.2f}")
                    print(f"Total: ${s['total']:.2f}")
                continue

            elif cmd == "alerts":
                alerts = tracker.get_all_alerts()
                print("\n--- PRICE DROP ALERTS ---")
                if not alerts:
                    print("No active alerts set.")
                else:
                    for a in alerts:
                        status = "TRIGGERED" if a["status"] == "triggered" else "WATCHING"
                        print(f"• [{status}] {a['product_title']}: Current ${a['current_price']:.2f} | Target ${a['target_price']:.2f}")
                continue

            elif cmd == "memory":
                print("\n--- CHROMADB MEMORY PROFILE ---")
                print(memory.format_memory_summary_for_prompt())
                continue

            elif cmd.startswith("simulate"):
                parts = user_input.split()
                if len(parts) >= 2:
                    pid = parts[1]
                    pct = float(parts[2]) if len(parts) > 2 else 15.0
                    res = tracker.simulate_price_drop(pid, drop_percentage=pct)
                    if res.get("success"):
                        print(f"\nPrice dropped on {res['title']}: ${res['old_price']:.2f} -> ${res['new_price']:.2f} (-{pct}%)")
                        if res.get("triggered_alerts"):
                            print("ALERT TRIGGERED for this product!")
                    else:
                        print(f"Error: {res.get('message')}")
                else:
                    print("Usage: simulate <product_id> [percentage]")
                continue

            elif cmd == "clear":
                history = []
                print("Session history cleared.")
                continue

            # Run agentic workflow
            print("\nAura is thinking...\n")
            res = agent.run(user_input, chat_history=history)
            
            if res.get("agent_steps"):
                print(f"[Tools Executed: {', '.join([s['tool'] for s in res['agent_steps']])}]")
            
            print(f"\nAura > {res['response']}")

            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": res["response"]})

        except KeyboardInterrupt:
            print("\nExiting Aura. Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    main()
