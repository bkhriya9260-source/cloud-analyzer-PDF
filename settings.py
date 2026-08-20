from typing import Dict, Any
from sqlalchemy.orm import Session
from subscriptions import get_user_plan_status

class SettingsUIController:
    def __init__(self, db: Session):
        self.db = db

    def get_user_settings_panel(self, user_id: int) -> Dict[str, Any]:
        """Displays user account settings, API keys, usage limits, and notification preferences"""
        plan_info = get_user_plan_status(user_id=user_id, db=self.db)

        return {
            "account_profile": {
                "user_id": user_id,
                "api_access_enabled": plan_info.get("api_access", False)
            },
            "subscription_overview": {
                "current_plan": plan_info.get("plan_tier"),
                "searches_used": plan_info.get("searches_used"),
                "max_searches_limit": plan_info.get("max_searches"),
                "monitored_stores_limit": plan_info.get("monitored_stores_limit")
            },
            "notification_preferences": {
                "email_alerts": True,
                "webhook_notifications": plan_info.get("api_access", False),
                "alert_triggers": ["PRICE_DROP", "NEW_WINNING_AD", "NEW_PRODUCT_LAUNCH"]
            }
        }