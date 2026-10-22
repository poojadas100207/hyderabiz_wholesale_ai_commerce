"""Price Drop Tracker and Alert Notification Engine."""

import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from src.config import PRICE_ALERTS_FILE
from src.catalog import get_product_by_id, update_product_price


class PriceTracker:
    """Tracks product price drops, manages alerts, and simulates market fluctuations."""

    def __init__(self, alerts_file: Optional[Path] = None):
        self.alerts_file = alerts_file or PRICE_ALERTS_FILE
        self.alerts: List[Dict[str, Any]] = []
        self._load_alerts()

    def _load_alerts(self):
        """Load alerts from persistent JSON file."""
        if self.alerts_file.exists():
            try:
                with open(self.alerts_file, "r", encoding="utf-8") as f:
                    self.alerts = json.load(f)
                    return
            except Exception as e:
                print(f"Error loading price alerts: {e}")
        self.alerts = []

    def _save_alerts(self):
        """Save alerts to persistent JSON file."""
        try:
            with open(self.alerts_file, "w", encoding="utf-8") as f:
                json.dump(self.alerts, f, indent=2)
        except Exception as e:
            print(f"Error saving price alerts: {e}")

    def add_alert(
        self,
        product_id: str,
        target_price: float,
        user_note: str = ""
    ) -> Dict[str, Any]:
        """Register a new price drop monitor for a product."""
        product = get_product_by_id(product_id)
        if not product:
            return {
                "success": False,
                "message": f"Product '{product_id}' not found in catalog."
            }

        current_price = product["price"]
        
        # Check if already tracking this product
        for a in self.alerts:
            if a["product_id"] == product["id"] and a["status"] == "active":
                a["target_price"] = target_price
                a["user_note"] = user_note or a.get("user_note", "")
                self._save_alerts()
                return {
                    "success": True,
                    "updated": True,
                    "alert": a,
                    "message": f"Updated existing price alert for {product['title']} to ${target_price:.2f}"
                }

        alert_id = f"ALT-{uuid.uuid4().hex[:8].upper()}"
        new_alert = {
            "alert_id": alert_id,
            "product_id": product["id"],
            "product_title": product["title"],
            "brand": product["brand"],
            "image_url": product.get("image_url", ""),
            "initial_price": current_price,
            "current_price": current_price,
            "target_price": round(target_price, 2),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": "active",
            "triggered_at": None,
            "triggered_price": None,
            "user_note": user_note,
            "notified": False
        }
        self.alerts.append(new_alert)
        self._save_alerts()

        # Check immediately in case current price already satisfies target
        self.check_alerts()

        return {
            "success": True,
            "updated": False,
            "alert": new_alert,
            "message": f"Price tracker set for '{product['title']}'! We will alert you when it drops to ${target_price:.2f} (Current: ${current_price:.2f})."
        }

    def remove_alert(self, alert_id: str) -> bool:
        """Remove a tracked alert by ID."""
        initial_len = len(self.alerts)
        self.alerts = [a for a in self.alerts if a["alert_id"] != alert_id]
        if len(self.alerts) < initial_len:
            self._save_alerts()
            return True
        return False

    def get_all_alerts(self) -> List[Dict[str, Any]]:
        """Return all tracked alerts with updated current prices."""
        for a in self.alerts:
            prod = get_product_by_id(a["product_id"])
            if prod:
                a["current_price"] = prod["price"]
        return self.alerts

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Return all currently active alerts."""
        return [a for a in self.get_all_alerts() if a["status"] == "active"]

    def check_alerts(self) -> List[Dict[str, Any]]:
        """Inspect all active alerts against latest catalog prices. Return newly triggered alerts."""
        newly_triggered = []
        for a in self.alerts:
            if a["status"] == "active":
                prod = get_product_by_id(a["product_id"])
                if prod:
                    curr = prod["price"]
                    a["current_price"] = curr
                    if curr <= a["target_price"]:
                        a["status"] = "triggered"
                        a["triggered_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                        a["triggered_price"] = curr
                        a["savings"] = round(a["initial_price"] - curr, 2)
                        newly_triggered.append(a)
        
        if newly_triggered:
            self._save_alerts()
        return newly_triggered

    def simulate_price_drop(self, product_id: str, drop_percentage: float = 15.0) -> Dict[str, Any]:
        """Simulate a flash deal or price cut on a product and check if alerts fire."""
        prod = get_product_by_id(product_id)
        if not prod:
            return {"success": False, "message": "Product not found."}
        
        old_price = prod["price"]
        new_price = round(old_price * (1.0 - (drop_percentage / 100.0)), 2)
        update_product_price(prod["id"], new_price)

        triggered = self.check_alerts()
        
        return {
            "success": True,
            "product_id": prod["id"],
            "title": prod["title"],
            "old_price": old_price,
            "new_price": new_price,
            "drop_percentage": drop_percentage,
            "triggered_alerts": [t for t in triggered if t["product_id"] == prod["id"]]
        }


# Singleton tracker instance
_tracker_instance: Optional[PriceTracker] = None

def get_price_tracker() -> PriceTracker:
    """Get or create singleton price tracker."""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = PriceTracker()
    return _tracker_instance
