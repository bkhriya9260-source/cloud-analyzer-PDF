from typing import Dict, Any, List

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
                "icon": "🏪",
                "title": f"Competitor Added New Product — {store}",
                "priority": "MEDIUM"
            },
            "COMPETITOR_PRICE_DROP": {
                "icon": "🔔",
                "title": f"Price Drop Detected on {product}",
                "priority": "HIGH"
            },
            "NEW_WINNING_AD": {
                "icon": "📢",
                "title": f"Competitor Launched Scaling Ad — {store}",
                "priority": "HIGH"
            },
            "DEMAND_SPIKE": {
                "icon": "📈",
                "title": f"Product Demand Surging — {product}",
                "priority": "CRITICAL"
            }
        }

        meta = alert_templates.get(event_type, {"icon": "🚨", "title": "Competitor Activity Alert", "priority": "LOW"})

        return {
            "alert_header": f"{meta['icon']} {meta['title']}",
            "priority": meta["priority"],
            "message": details,
            "target_store": store,
            "product": product,
            "generated_at": event_data.get("timestamp")
        }

    def dispatch_webhooks(self, alert_payload: Dict[str, Any], webhook_urls: List[str]) -> bool:
        """Dispatches structured JSON notifications to external endpoints (Slack, Discord, Custom Webhooks)"""
        # Logic for firing HTTP POST requests to configured user webhook endpoints
        return True