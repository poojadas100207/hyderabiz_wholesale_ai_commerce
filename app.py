"""Aura storefront - a local, Amazon-style shopping experience."""

import sys
import uuid
from datetime import datetime

import streamlit as st

from src.agent import ShoppingConciergeAgent
from src.catalog import (
    get_all_products,
    get_brands,
    get_categories,
    get_product_by_id,
    search_products,
)
from src.cart import get_shopping_cart
from src.config import get_api_key, set_api_key
from src.memory import get_memory_manager
from src.tracker import get_price_tracker

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

st.set_page_config(
    page_title="Aura Market",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    :root { --navy:#131921; --orange:#ff9900; --blue:#146eb4; --ink:#172033; --muted:#667085; }
    .stApp { background:#f3f4f6; font-family:Inter, sans-serif; }
    [data-testid="stSidebar"] { background:#fff; border-right:1px solid #e5e7eb; }
    .topbar { background:var(--navy); color:white; padding:18px 24px; border-radius:10px; margin-bottom:16px; }
    .brand { font-size:27px; font-weight:800; letter-spacing:-1px; }
    .brand span { color:var(--orange); }
    .tagline { color:#d1d5db; font-size:13px; margin-top:3px; }
    .hero { background:linear-gradient(105deg,#0f2742,#1769aa 62%,#35a1d6); border-radius:14px; padding:34px 40px; color:white; margin:12px 0 22px; }
    .hero h1 { font-size:36px; margin:0 0 8px; }
    .hero p { color:#e0f2fe; font-size:16px; margin:0; }
    .section-title { color:var(--ink); font-size:22px; font-weight:800; margin:22px 0 12px; }
    .card { background:#fff; border:1px solid #e5e7eb; border-radius:12px; padding:12px; height:100%; box-shadow:0 2px 5px #1018280a; }
    .card img { width:100%; height:185px; object-fit:contain; border-radius:8px; background:#f8fafc; }
    .product-title { color:#172033; font-weight:700; line-height:1.3; min-height:42px; margin-top:8px; }
    .muted { color:#667085; font-size:13px; }
    .price { color:#111827; font-size:24px; font-weight:800; }
    .old-price { color:#98a2b3; text-decoration:line-through; font-size:13px; margin-left:5px; }
    .deal { color:#b42318; font-size:12px; font-weight:700; }
    .pill { display:inline-block; background:#eaf4ff; color:#146eb4; padding:7px 12px; border-radius:20px; font-size:13px; font-weight:600; }
    .trust { background:#fff; border-radius:10px; border:1px solid #e5e7eb; padding:15px; text-align:center; color:#344054; }
    .summary { background:#fff; border:1px solid #e5e7eb; border-radius:12px; padding:22px; }
    </style>
    """,
    unsafe_allow_html=True,
)


def init_state():
    defaults = {
        "page": "Home",
        "selected_product": None,
        "search": "",
        "chat_history": [{
            "role": "assistant",
            "content": "Hi! I’m Aura. Tell me what you’re shopping for and I’ll find the best match.",
            "steps": [],
        }],
        "orders": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()
cart = get_shopping_cart()
tracker = get_price_tracker()
memory = get_memory_manager()


def money(value):
    return f"${value:,.2f}"


def open_product(product_id):
    st.session_state.selected_product = product_id
    st.session_state.page = "Product details"
    st.rerun()


def product_card(product, key_prefix):
    discount = (
        int((1 - product["price"] / product["original_price"]) * 100)
        if product.get("original_price", 0) > product["price"]
        else 0
    )
    st.markdown(
        f"""
        <div class="card">
          <img src="{product.get('image_url', '')}" alt="{product['title']}">
          <div class="muted">{product['brand']} · {product['category']}</div>
          <div class="product-title">{product['title']}</div>
          <div style="margin-top:7px"><span class="price">{money(product['price'])}</span>
          {"<span class='old-price'>" + money(product["original_price"]) + "</span>" if discount else ""}</div>
          {"<div class='deal'>Limited-time deal · " + str(discount) + "% off</div>" if discount else ""}
          <div class="muted">⭐ {product['rating']} · {product['review_count']:,} reviews</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Add to cart", key=f"{key_prefix}_add", use_container_width=True):
            result = cart.add_item(product["id"])
            st.toast(result["message"])
            st.rerun()
    with c2:
        if st.button("Details", key=f"{key_prefix}_details", use_container_width=True):
            open_product(product["id"])
    if st.button("♡ Watch price", key=f"{key_prefix}_watch", use_container_width=True):
        tracker.add_alert(product["id"], round(product["price"] * 0.9, 2))
        st.toast("Price watch added. We’ll alert you at a 10% drop.")
        st.rerun()


def render_products(products, key_prefix="product"):
    if not products:
        st.info("No products match those filters. Try a broader search or budget.")
        return
    for start in range(0, len(products), 4):
        row = products[start:start + 4]
        cols = st.columns(4)
        for index, product in enumerate(row):
            with cols[index]:
                product_card(product, f"{key_prefix}_{start + index}_{product['id']}")


def render_home():
    st.markdown(
        '<div class="hero"><h1>Shop smarter with Aura</h1>'
        '<p>Great products, honest reviews, and an AI concierge that remembers what you like.</p></div>',
        unsafe_allow_html=True,
    )
    c1, c2, c3, c4 = st.columns(4)
    for col, icon, title, body in [
        (c1, "🚚", "Fast delivery", "Free delivery on orders over $50"),
        (c2, "🔒", "Secure checkout", "Your local demo store keeps data private"),
        (c3, "↩️", "Easy returns", "Shop with confidence"),
        (c4, "🤖", "Ask Aura", "Personalized help whenever you need it"),
    ]:
        with col:
            st.markdown(f'<div class="trust"><b>{icon} {title}</b><br><span class="muted">{body}</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Shop by category</div>', unsafe_allow_html=True)
    category_cols = st.columns(min(5, len(get_categories())))
    for col, category in zip(category_cols, get_categories()):
        with col:
            if st.button(category, key=f"home_cat_{category}", use_container_width=True):
                st.session_state.search = ""
                st.session_state.page = "Shop"
                st.session_state.category = category
                st.rerun()
    st.markdown('<div class="section-title">Today’s deals</div>', unsafe_allow_html=True)
    deals = sorted(get_all_products(), key=lambda p: p.get("original_price", p["price"]) - p["price"], reverse=True)[:4]
    render_products(deals, "deal")
    st.markdown('<div class="section-title">Popular right now</div>', unsafe_allow_html=True)
    render_products(sorted(get_all_products(), key=lambda p: p["review_count"], reverse=True)[:4], "popular")


def render_shop():
    st.markdown('<div class="section-title">All products</div>', unsafe_allow_html=True)
    categories = ["All"] + get_categories()
    brands = ["All"] + get_brands()
    c1, c2, c3, c4 = st.columns([3, 1.3, 1.2, 1.1])
    with c1:
        query = st.text_input("Search", value=st.session_state.get("search", ""), placeholder="Search products, brands, or features", label_visibility="collapsed")
        st.session_state.search = query
    with c2:
        category = st.selectbox("Category", categories, index=categories.index(st.session_state.get("category", "All")) if st.session_state.get("category", "All") in categories else 0)
    with c3:
        brand = st.selectbox("Brand", brands)
    with c4:
        sort = st.selectbox("Sort", ["relevance", "price_asc", "price_desc", "rating", "popularity"], format_func=lambda x: {"price_asc": "Price: low", "price_desc": "Price: high", "rating": "Top rated", "popularity": "Popular", "relevance": "Relevance"}[x])
    max_price = st.slider("Maximum price", 50, 2000, 2000, 50)
    products = search_products(query, None if category == "All" else category, None if brand == "All" else brand, max_price=max_price, sort_by=sort, limit=20)
    st.caption(f"{len(products)} results")
    render_products(products, "shop")


def render_details():
    product = get_product_by_id(st.session_state.selected_product or "")
    if not product:
        st.session_state.page = "Shop"
        st.rerun()
    if st.button("← Back to shopping"):
        st.session_state.page = "Shop"
        st.rerun()
    left, right = st.columns([1, 1.2])
    with left:
        st.image(product["image_url"], use_container_width=True)
    with right:
        st.markdown(f"### {product['title']}")
        st.markdown(f"**{product['brand']}** · {product['category']} · ⭐ {product['rating']} ({product['review_count']:,} reviews)")
        st.markdown(f'<span class="price">{money(product["price"])}</span>', unsafe_allow_html=True)
        if product.get("original_price", product["price"]) > product["price"]:
            st.success(f"Save {money(product['original_price'] - product['price'])} today")
        st.write(product["description"])
        st.info(f"✓ {product.get('stock', 0)} in stock · Free delivery on orders over $50")
        quantity = st.number_input("Quantity", min_value=1, max_value=max(1, product.get("stock", 1)), value=1, key="detail_qty")
        if st.button("Add to cart", type="primary", use_container_width=True):
            cart.add_item(product["id"], quantity)
            st.success("Added to your cart.")
        if st.button("Watch for a 10% price drop", use_container_width=True):
            tracker.add_alert(product["id"], round(product["price"] * 0.9, 2))
            st.success("Price watch added.")
    st.markdown("---")
    st.markdown("### Product information")
    specs = product.get("specs", {})
    if specs:
        st.dataframe([{"Specification": key, "Details": value} for key, value in specs.items()], hide_index=True, use_container_width=True)
    st.markdown("### Customer reviews")
    for review in product.get("reviews", [])[:3]:
        with st.container(border=True):
            st.markdown(f"**{review['title']}** · {'⭐' * review['rating']} · {review['author']}")
            st.caption(review["text"])
            st.write(f"**Pros:** {review['pros']}  \n**Cons:** {review['cons']}")


def render_cart():
    summary = cart.get_summary()
    st.markdown('<div class="section-title">Shopping cart</div>', unsafe_allow_html=True)
    if not summary["items"]:
        st.info("Your cart is empty. Find something you love in the shop.")
        if st.button("Continue shopping", type="primary"):
            st.session_state.page = "Shop"
            st.rerun()
        return
    items_col, summary_col = st.columns([1.7, 1])
    with items_col:
        for item in summary["items"]:
            with st.container(border=True):
                image, details, actions = st.columns([1, 3, 1])
                with image:
                    st.image(item["image_url"], width=110)
                with details:
                    st.markdown(f"**{item['title']}**")
                    st.caption(f"{item['brand']} · {money(item['unit_price'])} each")
                    st.markdown(f"Item total: **{money(item['item_total'])}**")
                with actions:
                    if st.button("＋", key=f"plus_{item['id']}", use_container_width=True):
                        cart.add_item(item["id"])
                        st.rerun()
                    st.caption(f"{item['quantity']} in cart")
                    if st.button("−", key=f"minus_{item['id']}", use_container_width=True):
                        cart.remove_item(item["id"], 1)
                        st.rerun()
                    if st.button("Remove", key=f"remove_{item['id']}", use_container_width=True):
                        cart.remove_item(item["id"])
                        st.rerun()
    with summary_col:
        st.markdown('<div class="summary">', unsafe_allow_html=True)
        st.markdown("### Order summary")
        st.write(f"Subtotal: **{money(summary['subtotal'])}**")
        promo = st.text_input("Promo code", placeholder="Try WELCOME10")
        if st.button("Apply promo", use_container_width=True):
            result = cart.apply_promo(promo)
            (st.success if result["success"] else st.error)(result["message"])
            st.rerun()
        if summary["promo_code"]:
            st.write(f"Discount ({summary['promo_code']}): **-{money(summary['discount_amount'])}**")
        st.write(f"Shipping: **{'FREE' if summary['shipping'] == 0 else money(summary['shipping'])}**")
        st.write(f"Estimated tax: **{money(summary['tax'])}**")
        st.markdown(f"## Total: {money(summary['total'])}")
        st.markdown("</div>", unsafe_allow_html=True)
        if st.button("Proceed to checkout", type="primary", use_container_width=True):
            st.session_state.page = "Checkout"
            st.rerun()


def render_checkout():
    summary = cart.get_summary()
    if not summary["items"]:
        st.session_state.page = "Cart"
        st.rerun()
    st.markdown('<div class="section-title">Secure checkout</div>', unsafe_allow_html=True)
    left, right = st.columns([1.4, 1])
    with left:
        with st.form("checkout_form"):
            st.markdown("#### Delivery address")
            name = st.text_input("Full name")
            address = st.text_input("Street address")
            city = st.text_input("City")
            postal = st.text_input("Postal code")
            st.markdown("#### Payment")
            payment = st.selectbox("Payment method", ["Visa ending in 4242", "Cash on delivery"])
            submitted = st.form_submit_button("Place your order", type="primary", use_container_width=True)
        if submitted:
            if not all([name.strip(), address.strip(), city.strip(), postal.strip()]):
                st.error("Please complete your delivery address.")
            else:
                order_id = f"AURA-{uuid.uuid4().hex[:8].upper()}"
                st.session_state.orders.insert(0, {"id": order_id, "date": datetime.now().strftime("%d %b %Y, %I:%M %p"), "total": summary["total"], "items": summary["total_items_count"], "status": "Order confirmed"})
                cart.clear()
                st.session_state.last_order = order_id
                st.balloons()
                st.success(f"Order {order_id} confirmed. We’ll deliver to {city}.")
                st.session_state.page = "Orders"
                st.rerun()
    with right:
        st.markdown("### Arrives in 3–5 business days")
        st.markdown(f"### Total: {money(summary['total'])}")
        st.caption(f"Payment: {payment if 'payment' in locals() else 'Secure payment'}")


def render_orders():
    st.markdown('<div class="section-title">Your orders</div>', unsafe_allow_html=True)
    if not st.session_state.orders:
        st.info("You haven’t placed any orders yet.")
        return
    for order in st.session_state.orders:
        with st.container(border=True):
            st.markdown(f"**{order['status']}** · Order **{order['id']}**")
            st.caption(f"{order['date']} · {order['items']} item(s) · Total {money(order['total'])}")


def render_watchlist():
    st.markdown('<div class="section-title">Price watchlist</div>', unsafe_allow_html=True)
    alerts = tracker.get_all_alerts()
    if not alerts:
        st.info("Watch a product to get notified when its price drops.")
        return
    for alert in alerts:
        with st.container(border=True):
            image, info, action = st.columns([1, 4, 1])
            with image:
                st.image(alert.get("image_url", ""), width=100)
            with info:
                st.markdown(f"**{alert['product_title']}**")
                st.write(f"Current: **{money(alert['current_price'])}** · Target: **{money(alert['target_price'])}**")
                st.caption("🎉 Target reached — buy now!" if alert["status"] == "triggered" else "Watching for your target price")
            with action:
                if st.button("Remove", key=f"watch_remove_{alert['alert_id']}"):
                    tracker.remove_alert(alert["alert_id"])
                    st.rerun()


def render_chat():
    st.markdown('<div class="section-title">Ask Aura</div>', unsafe_allow_html=True)
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    prompt = st.chat_input("Ask for recommendations, reviews, comparisons, or cart help")
    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt, "steps": []})
        with st.spinner("Aura is checking the catalog..."):
            result = st.session_state.agent.run(prompt, chat_history=st.session_state.chat_history[:-1])
        st.session_state.chat_history.append({"role": "assistant", "content": result["response"], "steps": result.get("agent_steps", [])})
        st.rerun()


with st.sidebar:
    st.markdown("## 🛒 Aura Market")
    st.caption("Your intelligent shopping destination")
    pages = ["Home", "Shop", "Cart", "Orders", "Price watchlist", "Ask Aura"]
    selected_page = st.radio("Browse", pages, index=pages.index(st.session_state.page) if st.session_state.page in pages else 0)
    if selected_page != st.session_state.page:
        st.session_state.page = selected_page
        st.session_state.selected_product = None
        st.rerun()
    cart_summary = cart.get_summary()
    st.divider()
    st.metric("Cart", f"{cart_summary['total_items_count']} item(s)", money(cart_summary["total"]))
    st.caption("Free delivery on orders over $50")
    with st.expander("Concierge settings"):
        api_key = st.text_input("Gemini API key", value=get_api_key(), type="password")
        if api_key != get_api_key():
            set_api_key(api_key, persist_to_env=True)
            st.session_state.agent = ShoppingConciergeAgent()
            st.success("Settings saved")

st.markdown('<div class="topbar"><div class="brand">aura<span>market</span></div><div class="tagline">Everything you need, with a little more intelligence.</div></div>', unsafe_allow_html=True)

if "agent" not in st.session_state:
    st.session_state.agent = ShoppingConciergeAgent()

if st.session_state.page == "Home":
    render_home()
elif st.session_state.page == "Shop":
    render_shop()
elif st.session_state.page == "Product details":
    render_details()
elif st.session_state.page == "Cart":
    render_cart()
elif st.session_state.page == "Checkout":
    render_checkout()
elif st.session_state.page == "Orders":
    render_orders()
elif st.session_state.page == "Price watchlist":
    render_watchlist()
elif st.session_state.page == "Ask Aura":
    render_chat()
