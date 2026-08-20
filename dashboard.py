from typing import Dict, Any, List
from sqlalchemy.orm import Session
from database import ProductModel, StoreModel, OpportunityScoreModel, Alert

class DashboardController:
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def get_overview_metrics(self) -> Dict[str, Any]:
        """Calculates macro metrics for the main customer overview panel"""
        total_discovered = self.db.query(ProductModel).count()
        monitored_stores = self.db.query(StoreModel).filter(StoreModel.is_monitored == True).count()
        unread_alerts = self.db.query(Alert).filter(Alert.user_id == self.user_id, Alert.is_read == False).count()

        # High Opportunity Products (Score >= 80)
        high_opp_count = (
            self.db.query(OpportunityScoreModel)
            .filter(OpportunityScoreModel.score >= 80)
            .count()
        )

        return {
            "summary_cards": {
                "total_products_discovered": total_discovered,
                "high_opportunity_products": high_opp_count,
                "monitored_competitors": monitored_stores,
                "unread_alerts_count": unread_alerts
            },
            "system_status": "Live Real-Time Monitoring Active"
        }