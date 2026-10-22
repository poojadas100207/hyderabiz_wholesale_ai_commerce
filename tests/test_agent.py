"""Comprehensive test suite for the Autonomous Shopping Concierge Agent."""

import pytest
import sys
from pathlib import Path

# Fix Windows console UTF-8 output
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.catalog import (
    get_all_products,
    get_product_by_id,
    search_products,
    get_categories,
    get_brands
)
from src.memory import get_memory_manager
from src.tracker import get_price_tracker
from src.cart import get_shopping_cart
from src.tools import (
    search_products_tool,
    get_product_details_tool,
    summarize_reviews_tool,
    compare_products_tool,
    track_price_drop_tool,
    manage_cart_tool
)
from src.agent import ShoppingConciergeAgent


def test_catalog_retrieval_and_filtering():
    """Verify products catalog loading, category filtering, and price bounds."""
    products = get_all_products()
    assert len(products) >= 8

    # Category filter
    audio_prods = search_products(category="Audio & Headphones")
    assert len(audio_prods) >= 2
    assert all(p["category"] == "Audio & Headphones" for p in audio_prods)

    # Price ceiling filter
    cheap_prods = search_products(max_price=120.0)
    assert len(cheap_prods) >= 1
    assert all(p["price"] <= 120.0 for p in cheap_prods)


def test_chroma_vector_memory():
    """Verify ChromaDB episodic memory storage, semantic search, and user profile."""
    memory = get_memory_manager()
    
    # Update profile
    memory.update_preference("preferred_brands", "Sony")
    memory.update_preference("max_budget", 400.0)
    profile = memory.get_user_profile()
    assert "Sony" in profile["preferred_brands"]
    assert profile["max_budget"] == 400.0

    # Record and recall episodic memory
    memory.record_interaction("user", "I need noise cancelling headphones for daily train travel", topic="travel_audio")
    recalled = memory.recall_relevant_memories("train commute audio", n_results=2)
    assert len(recalled) > 0

    # Semantic product search via ChromaDB
    semantic_res = memory.search_products_semantically("comfortable runner running marathon", n_results=3)
    assert len(semantic_res) > 0
    matched_ids = [p["id"] for p in semantic_res]
    assert any(pid in ["PROD-301", "PROD-302"] for pid in matched_ids)


def test_review_summarization_tool():
    """Verify review synthesis extracts pros, cons, and customer sentiments."""
    out = summarize_reviews_tool.invoke({"product_id": "PROD-101"})
    assert "Review Synthesis for Sony WH-1000XM5" in out
    assert "Overall Sentiment:" in out
    assert "Top Praises:" in out
    assert "Criticisms & Considerations:" in out
    assert "Concierge Buying Advice:" in out


def test_product_comparison_tool():
    """Verify side-by-side comparison between two items."""
    out = compare_products_tool.invoke({"product_id_1": "PROD-101", "product_id_2": "PROD-102"})
    assert "Side-by-Side Comparison" in out
    assert "Pricing & Value" in out
    assert "Recommendation Verdict" in out


def test_price_tracker_and_simulation():
    """Verify setting an alert and triggering a price drop."""
    tracker = get_price_tracker()
    
    # Track an item
    alert_res = tracker.add_alert(product_id="PROD-103", target_price=85.00, user_note="Test Alert")
    assert alert_res["success"] is True

    # Drop price below target
    sim_res = tracker.simulate_price_drop(product_id="PROD-103", drop_percentage=20.0)
    assert sim_res["success"] is True
    assert sim_res["new_price"] < 85.00
    assert len(sim_res["triggered_alerts"]) >= 1

    # Check alert status updated
    all_alerts = tracker.get_all_alerts()
    matched = [a for a in all_alerts if a["product_id"] == "PROD-103"]
    assert len(matched) > 0
    assert matched[0]["status"] == "triggered"
    assert matched[0]["savings"] > 0


def test_shopping_cart_and_promos():
    """Verify cart addition, discount coupon calculation, taxes, and shipping."""
    cart = get_shopping_cart()
    cart.clear()

    # Add item
    add_res = cart.add_item("PROD-301", quantity=1)
    assert add_res["success"] is True
    
    # Summary
    s = cart.get_summary()
    assert s["total_items_count"] == 1
    assert s["subtotal"] > 0
    
    # Apply promo
    promo_res = cart.apply_promo("WELCOME10")
    assert promo_res["success"] is True
    s_promo = cart.get_summary()
    assert s_promo["discount_amount"] > 0
    assert s_promo["total"] < s["total"]

    # Clear
    cart.clear()
    assert cart.get_summary()["total_items_count"] == 0


def test_agentic_workflow_execution():
    """Verify the autonomous concierge agent processes requests end-to-end."""
    agent = ShoppingConciergeAgent()
    
    # Test product query
    res = agent.run("Find running shoes under $130")
    assert "response" in res
    assert len(res["response"]) > 0
    assert "agent_steps" in res
    assert len(res["agent_steps"]) > 0

    # Test review query
    res_rev = agent.run("What are the reviews of Dyson V12?")
    assert "response" in res_rev
    assert "Dyson" in res_rev["response"] or "Review" in res_rev["response"]
