"""Shopping Cart Management with subtotal, promo discounts, tax, and persistence."""

import json
from typing import Dict, Any, List, Optional
from src.config import CART_FILE
from src.catalog import get_product_by_id

VALID_PROMOS = {
    "WELCOME10": 0.10,
    "CONCIERGE20": 0.20,
    "FLASH15": 0.15
}


class ShoppingCart:
    """Manages items added to cart, discounts, tax, and checkout estimation."""

    def __init__(self):
        self.file_path = CART_FILE
        self.cart_data: Dict[str, Any] = {"items": {}, "promo_code": None}
        self._load()

    def _load(self):
        if self.file_path.exists():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self.cart_data = json.load(f)
                    return
            except Exception:
                pass
        self.cart_data = {"items": {}, "promo_code": None}

    def _save(self):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.cart_data, f, indent=2)
        except Exception as e:
            print(f"Error saving cart: {e}")

    def add_item(self, product_id: str, quantity: int = 1) -> Dict[str, Any]:
        """Add or increment item in cart."""
        product = get_product_by_id(product_id)
        if not product:
            return {"success": False, "message": f"Product '{product_id}' not found."}
        
        pid = product["id"]
        current_qty = self.cart_data["items"].get(pid, 0)
        self.cart_data["items"][pid] = current_qty + max(1, quantity)
        self._save()
        return {
            "success": True,
            "message": f"Added {quantity}x '{product['title']}' to your cart.",
            "cart_summary": self.get_summary()
        }

    def remove_item(self, product_id: str, quantity: Optional[int] = None) -> Dict[str, Any]:
        """Remove or decrement item from cart."""
        product = get_product_by_id(product_id)
        pid = product["id"] if product else product_id
        if pid not in self.cart_data["items"]:
            return {"success": False, "message": "Item not in cart."}

        if quantity is None or quantity >= self.cart_data["items"][pid]:
            del self.cart_data["items"][pid]
            msg = f"Removed item from cart."
        else:
            self.cart_data["items"][pid] -= quantity
            msg = f"Reduced quantity by {quantity}."

        self._save()
        return {
            "success": True,
            "message": msg,
            "cart_summary": self.get_summary()
        }

    def apply_promo(self, code: str) -> Dict[str, Any]:
        """Apply promotional discount code."""
        clean_code = code.strip().upper()
        if clean_code in VALID_PROMOS:
            self.cart_data["promo_code"] = clean_code
            self._save()
            return {
                "success": True,
                "message": f"Promo code '{clean_code}' applied! You saved {int(VALID_PROMOS[clean_code]*100)}% on your order.",
                "cart_summary": self.get_summary()
            }
        return {
            "success": False,
            "message": f"Promo code '{code}' is invalid or expired. Try 'WELCOME10' or 'CONCIERGE20'."
        }

    def clear(self):
        """Empty the cart."""
        self.cart_data = {"items": {}, "promo_code": None}
        self._save()

    def get_summary(self) -> Dict[str, Any]:
        """Calculate detailed financial breakdown of the cart."""
        items_detail = []
        subtotal = 0.0

        for pid, qty in self.cart_data["items"].items():
            prod = get_product_by_id(pid)
            if prod:
                item_total = prod["price"] * qty
                subtotal += item_total
                items_detail.append({
                    "id": prod["id"],
                    "title": prod["title"],
                    "brand": prod["brand"],
                    "unit_price": prod["price"],
                    "quantity": qty,
                    "item_total": round(item_total, 2),
                    "image_url": prod.get("image_url", "")
                })

        promo_code = self.cart_data.get("promo_code")
        discount_rate = VALID_PROMOS.get(promo_code, 0.0) if promo_code else 0.0
        discount_amount = round(subtotal * discount_rate, 2)
        
        discounted_subtotal = max(0.0, subtotal - discount_amount)
        # Free shipping over $50, else $9.99
        shipping = 0.0 if (discounted_subtotal >= 50.0 or subtotal == 0) else 9.99
        # Estimated tax ~ 8.25%
        tax = round(discounted_subtotal * 0.0825, 2) if subtotal > 0 else 0.0
        total = round(discounted_subtotal + shipping + tax, 2)

        return {
            "items": items_detail,
            "total_items_count": sum(self.cart_data["items"].values()),
            "subtotal": round(subtotal, 2),
            "promo_code": promo_code,
            "discount_amount": discount_amount,
            "shipping": shipping,
            "tax": tax,
            "total": total
        }


_cart_instance: Optional[ShoppingCart] = None

def get_shopping_cart() -> ShoppingCart:
    """Get singleton shopping cart instance."""
    global _cart_instance
    if _cart_instance is None:
        _cart_instance = ShoppingCart()
    return _cart_instance
