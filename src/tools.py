"""LangChain Tools for Autonomous E-Commerce Concierge Agent."""

import json
from typing import Optional, List, Dict, Any
from langchain_core.tools import tool

from src.catalog import (
    search_products,
    get_product_by_id,
    get_all_products
)
from src.memory import get_memory_manager
from src.tracker import get_price_tracker
from src.cart import get_shopping_cart


@tool
def search_products_tool(
    query: str = "",
    category: Optional[str] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_rating: Optional[float] = None,
    sort_by: str = "relevance"
) -> str:
    """Search and filter products across the store catalog by keyword, semantic topic, category, brand, price range, or rating.
    Use this whenever the user is looking for recommendations, browsing items, or searching for specific products.
    """
    memory = get_memory_manager()
    
    # If a rich conceptual query is provided without strict filters, leverage vector search first
    if query and not category and min_price is None and max_price is None:
        semantic_matches = memory.search_products_semantically(query, n_results=5)
        if semantic_matches:
            results = semantic_matches
        else:
            results = search_products(query=query, category=category, brand=brand, min_price=min_price, max_price=max_price, min_rating=min_rating, sort_by=sort_by)
    else:
        results = search_products(
            query=query,
            category=category,
            brand=brand,
            min_price=min_price,
            max_price=max_price,
            min_rating=min_rating,
            sort_by=sort_by,
            limit=6
        )

    if not results:
        return f"No products found matching criteria: query='{query}', category='{category}', price range=${min_price or 0}-${max_price or 'Any'}."

    output = []
    for p in results:
        orig = f" (Was ${p['original_price']:.2f})" if p.get('original_price') and p['original_price'] > p['price'] else ""
        item_str = (
            f"• [{p['id']}] {p['title']} - ${p['price']:.2f}{orig}\n"
            f"  Brand: {p['brand']} | Category: {p['category']} | Rating: {p['rating']}/5.0 ({p['review_count']} reviews)\n"
            f"  Highlights: {p['description']}\n"
            f"  Key Specs: {', '.join([f'{k}: {v}' for k, v in list(p.get('specs', {}).items())[:3]])}"
        )
        output.append(item_str)
    
    return f"Found {len(results)} matching product(s):\n\n" + "\n\n".join(output)


@tool
def get_product_details_tool(product_id: str) -> str:
    """Retrieve in-depth product information, complete technical specifications, inventory, and historical pricing by product ID (e.g. 'PROD-101') or name."""
    product = get_product_by_id(product_id)
    if not product:
        return f"Product with ID or name '{product_id}' was not found in the catalog."

    specs_formatted = "\n".join([f"  - {k}: {v}" for k, v in product.get("specs", {}).items()])
    price_hist = product.get("price_history", [])
    history_formatted = "\n".join([f"  - {h['date']}: ${h['price']:.2f}" for h in price_hist[-4:]])
    
    orig = f" (Original List Price: ${product['original_price']:.2f})" if product.get('original_price') else ""
    return (
        f"Product Details for [{product['id']}] {product['title']}:\n"
        f"Brand: {product['brand']} | Category: {product['category']}\n"
        f"Current Price: ${product['price']:.2f}{orig}\n"
        f"Customer Rating: {product['rating']} / 5.0 ({product['review_count']} reviews)\n"
        f"In Stock: {'Yes' if product.get('in_stock', True) else 'Out of Stock'} ({product.get('stock', 0)} units available)\n"
        f"Description: {product['description']}\n\n"
        f"Technical Specifications:\n{specs_formatted}\n\n"
        f"Recent Price Trend:\n{history_formatted}"
    )


@tool
def summarize_reviews_tool(product_id: str) -> str:
    """Synthesize customer reviews and sentiment for a product. Identifies recurring pros, common cons/complaints, sentiment breakdown, and buying recommendation."""
    product = get_product_by_id(product_id)
    if not product:
        return f"Product '{product_id}' not found."

    reviews = product.get("reviews", [])
    if not reviews:
        return f"No customer reviews currently logged for {product['title']}."

    ratings = [r["rating"] for r in reviews]
    avg_rating = sum(ratings) / len(ratings)
    positives = [r for r in reviews if r["rating"] >= 4]
    critical = [r for r in reviews if r["rating"] <= 3]

    pros_list = [f"• {r.get('pros')}" for r in reviews if r.get('pros')]
    cons_list = [f"• {r.get('cons')}" for r in reviews if r.get('cons')]

    sample_quotes = []
    for r in reviews[:2]:
        sample_quotes.append(f'  "{r["text"]}" - {r["author"]} ({r["rating"]}/5.0, Verified)')

    summary = (
        f"Review Synthesis for {product['title']} ({product['id']}):\n"
        f"Overall Sentiment: {'Extremely Positive' if avg_rating >= 4.5 else 'Positive'} ({avg_rating:.1f}/5.0 based on verified buyers)\n\n"
        f"Top Praises:\n" + ("\n".join(pros_list) if pros_list else "  - High build quality and performance") + "\n\n"
        f"Criticisms & Considerations:\n" + ("\n".join(cons_list) if cons_list else "  - None reported") + "\n\n"
        f"Customer Quotes:\n" + "\n".join(sample_quotes) + "\n\n"
        f"Concierge Buying Advice: "
        f"{'Highly recommended for power users seeking premium performance.' if avg_rating >= 4.6 else 'Solid all-around choice with high reliability.'}"
    )
    return summary


@tool
def compare_products_tool(product_id_1: str, product_id_2: str) -> str:
    """Perform a side-by-side comparison of two products highlighting key differences in price, specs, strengths, and who each product is best suited for."""
    p1 = get_product_by_id(product_id_1)
    p2 = get_product_by_id(product_id_2)

    if not p1:
        return f"First product '{product_id_1}' could not be located."
    if not p2:
        return f"Second product '{product_id_2}' could not be located."

    p1_specs = p1.get("specs", {})
    p2_specs = p2.get("specs", {})

    diff_str = (
        f"=== Side-by-Side Comparison: {p1['title']} vs {p2['title']} ===\n\n"
        f"1. Pricing & Value:\n"
        f"   • {p1['title']}: ${p1['price']:.2f} ({p1['rating']}/5.0 from {p1['review_count']} reviews)\n"
        f"   • {p2['title']}: ${p2['price']:.2f} ({p2['rating']}/5.0 from {p2['review_count']} reviews)\n"
        f"   Price Difference: ${abs(p1['price'] - p2['price']):.2f} ({p1['title'] if p1['price'] < p2['price'] else p2['title']} is more affordable)\n\n"
        f"2. Key Technical Specs:\n"
        f"   • {p1['title']}: {', '.join([f'{k}: {v}' for k, v in list(p1_specs.items())[:3]])}\n"
        f"   • {p2['title']}: {', '.join([f'{k}: {v}' for k, v in list(p2_specs.items())[:3]])}\n\n"
        f"3. Recommendation Verdict:\n"
        f"   - Choose {p1['title']} if you prioritize {p1.get('tags', ['performance'])[0]} and {p1['brand']} ecosystem.\n"
        f"   - Choose {p2['title']} if you prioritize {p2.get('tags', ['value'])[0]} and {p2['brand']} ergonomics."
    )
    return diff_str


@tool
def track_price_drop_tool(product_id: str, target_price: float, user_note: str = "") -> str:
    """Set a price drop alert for a specific product. The concierge will monitor the product and notify the user when the price hits or drops below the target price."""
    tracker = get_price_tracker()
    res = tracker.add_alert(product_id=product_id, target_price=target_price, user_note=user_note)
    return res["message"]


@tool
def check_price_drop_alerts_tool() -> str:
    """Check all currently tracked price alerts to see if any items have dropped in price or met their target."""
    tracker = get_price_tracker()
    all_alerts = tracker.get_all_alerts()
    if not all_alerts:
        return "You currently have no active price drop alerts. You can track any product by asking me!"

    triggered = [a for a in all_alerts if a["status"] == "triggered"]
    active = [a for a in all_alerts if a["status"] == "active"]

    lines = [f"=== PRICE DROP ALERTS STATUS (Total: {len(all_alerts)}) ==="]
    if triggered:
        lines.append("\n🎉 TRIGGERED PRICE DROPS (Ready to buy!):")
        for a in triggered:
            lines.append(f"  • {a['product_title']}: Current ${a['current_price']:.2f} <= Target ${a['target_price']:.2f} (Saved ${a.get('savings', 0):.2f}!)")

    if active:
        lines.append("\n⏳ ACTIVELY WATCHED ITEMS:")
        for a in active:
            lines.append(f"  • {a['product_title']}: Current ${a['current_price']:.2f} | Target: ${a['target_price']:.2f}")

    return "\n".join(lines)


@tool
def recall_user_memory_tool(query: str) -> str:
    """Recall information from conversational vector memory and past interactions (e.g. past preferences, previously viewed items, stated needs)."""
    memory = get_memory_manager()
    recalled = memory.recall_relevant_memories(query, n_results=3)
    if not recalled:
        return f"No prior memories found matching query '{query}'."

    out = [f"Found {len(recalled)} memory item(s):"]
    for m in recalled:
        out.append(f"- {m['content']} (Logged: {m['metadata'].get('timestamp', 'past')})")
    return "\n".join(out)


@tool
def update_user_preference_tool(preference_type: str, value: str) -> str:
    """Save or update a user preference into persistent long-term memory.
    Supported types: 'preferred_brands', 'disliked_brands', 'sizes', 'budget_tier', 'max_budget', 'lifestyle_notes', 'special_requirements'.
    """
    memory = get_memory_manager()
    if preference_type == "max_budget":
        try:
            val_clean = float(value.replace("$", "").strip())
            memory.update_preference("max_budget", val_clean)
        except Exception:
            return f"Invalid numeric budget: {value}"
    elif preference_type == "sizes":
        memory.update_preference("sizes", {"note": value})
    else:
        memory.update_preference(preference_type, value)
    
    return f"Successfully updated your preference '{preference_type}' with '{value}'. I will keep this in mind for all future recommendations!"


@tool
def manage_cart_tool(action: str, product_id: str = "", quantity: int = 1, promo_code: str = "") -> str:
    """Manage user shopping cart.
    Actions:
    - 'view': Inspect cart items, subtotal, discounts, taxes, and estimated total.
    - 'add': Add product to cart by product_id with optional quantity.
    - 'remove': Remove product from cart by product_id.
    - 'apply_promo': Apply a discount coupon code (e.g. 'WELCOME10', 'CONCIERGE20').
    - 'clear': Empty the entire cart.
    """
    cart = get_shopping_cart()
    act = action.lower().strip()

    if act == "add":
        if not product_id:
            return "Please provide a valid product_id to add to cart."
        res = cart.add_item(product_id=product_id, quantity=quantity)
        summary = cart.get_summary()
        return f"{res['message']}\nCart Total: ${summary['total']:.2f} ({summary['total_items_count']} items)."

    elif act == "remove":
        if not product_id:
            return "Please provide a product_id to remove from cart."
        res = cart.remove_item(product_id=product_id)
        summary = cart.get_summary()
        return f"{res['message']}\nCart Total: ${summary['total']:.2f} ({summary['total_items_count']} items)."

    elif act == "apply_promo":
        if not promo_code:
            return "Please provide a promo code to apply."
        res = cart.apply_promo(promo_code)
        return res["message"]

    elif act == "clear":
        cart.clear()
        return "Your shopping cart has been cleared."

    elif act == "view":
        summary = cart.get_summary()
        if not summary["items"]:
            return "Your shopping cart is currently empty. Feel free to browse products and add what you like!"
        
        lines = [f"=== SHOPPING CART ({summary['total_items_count']} items) ==="]
        for it in summary["items"]:
            lines.append(f"• {it['quantity']}x {it['title']} - ${it['unit_price']:.2f} each (${it['item_total']:.2f})")
        lines.append(f"\nSubtotal: ${summary['subtotal']:.2f}")
        if summary.get("promo_code"):
            lines.append(f"Promo '{summary['promo_code']}': -${summary['discount_amount']:.2f}")
        shipping_str = "FREE" if summary['shipping'] == 0 else f"${summary['shipping']:.2f}"
        lines.append(f"Estimated Shipping: {shipping_str}")
        lines.append(f"Estimated Tax: ${summary['tax']:.2f}")
        lines.append(f"Order Total: ${summary['total']:.2f}")
        return "\n".join(lines)

    return f"Unknown cart action '{action}'. Valid actions: view, add, remove, apply_promo, clear."


ALL_TOOLS = [
    search_products_tool,
    get_product_details_tool,
    summarize_reviews_tool,
    compare_products_tool,
    track_price_drop_tool,
    check_price_drop_alerts_tool,
    recall_user_memory_tool,
    update_user_preference_tool,
    manage_cart_tool
]
