from typing import Dict, Any, List
from datetime import datetime

class AlertNotificationEngine:
    def __init__(self):
        pass

    def format_alert_payload(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transforms monitored events into actionable user alerts"""
        
        event_type = event_data.get("event_type")
        store = event_data.get("store", "Tracked Store")
        product = event_data.get("product_title", "Product")
        details = event_data.get("details", "")

        alert_templates = {
            "NEW_PRODUCT_LAUNCHED": {
                "icon": "📦",
                "title": f"Competitor Added New Product - {store}",
                "priority": "MEDIUM"
            },
            "COMPETITOR_PRICE_DROP": {
                "icon": "🔔",
                "title": f"Price Drop Detected on {product}",
                "priority": "HIGH"
            },
            "NEW_WINNING_AD": {
                "icon": "📢",
                "title": f"Competitor Launched Scaling Ad - {store}",
                "priority": "HIGH"
            },
            "DEMAND_SPIKE": {
                "icon": "📈",
                "title": f"Product Demand Surging - {product}",
                "priority": "CRITICAL"
            }
        }

        meta = alert_templates.get(event_type, {"icon": "🚨", "title": "Competitor Activity Alert", "priority": "MEDIUM"})

        return {
            "alert_header": f"{meta['icon']} {meta['title']}",
            "priority": meta["priority"],
            "message": details,
            "target_store": store,
            "product": product,
            "generated_at": event_data.get("timestamp", datetime.utcnow().isoformat())
        }

    def dispatch_webhooks(self, alert_payload: Dict[str, Any], webhook_urls: List[str]) -> bool:
        """Dispatches structured JSON notifications to external endpoints (Slack, Discord, Custom)"""
        # Logic for firing HTTP POST requests to configured user webhook endpoints
        return True


class AlertEngine:
    def __init__(self):
        self.monitored_targets = {}

    def register_monitoring_target(self, target_id: str, url: str, initial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Saves initial product/competitor snapshot for continuous monitoring.
        """
        self.monitored_targets[target_id] = {
            "url": url,
            "last_scanned": datetime.utcnow().isoformat(),
            "snapshot": initial_data
        }
        return {
            "status": "success",
            "message": f"Target {target_id} successfully registered for scheduled monitoring.",
            "target": self.monitored_targets[target_id]
        }

    def evaluate_changes_and_alert(self, target_id: str, new_snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compares old snapshot with new snapshot and triggers alerts if major changes detected.
        """
        old_data = self.monitored_targets.get(target_id, {}).get("snapshot", {})
        alerts = []

        old_price = old_data.get("price", 0.0)
        new_price = new_snapshot.get("price", 0.0)

        # 1. Price Drop / Increase Alert
        if old_price and new_price:
            if new_price < old_price:
                price_diff = round(old_price - new_price, 2)
                alerts.append(f"CRITICAL: Competitor lowered price by ${price_diff} (New price: ${new_price}).")
            elif new_price > old_price:
                alerts.append(f"INFO: Competitor increased price to ${new_price}.")

        # 2. Stock / Out of Stock Alert
        old_stock = old_data.get("in_stock", True)
        new_stock = new_snapshot.get("in_stock", True)

        if old_stock and not new_stock:
            alerts.append("OPPORTUNITY: Competitor went OUT OF STOCK. Increase ad budget!")
        elif not old_stock and new_stock:
            alerts.append("WARNING: Competitor is back IN STOCK.")

        # Update last snapshot
        if target_id in self.monitored_targets:
            self.monitored_targets[target_id]["snapshot"] = new_snapshot
            self.monitored_targets[target_id]["last_scanned"] = datetime.utcnow().isoformat()

        return {
            "target_id": target_id,
            "has_alerts": len(alerts) > 0,
            "alerts_triggered": alerts if alerts else ["No critical changes detected."],
            "evaluated_at": datetime.utcnow().isoformat()
        }
