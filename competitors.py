from typing import Dict, Any, List
from sqlalchemy.orm import Session
from database import StoreModel

class CompetitorUIController:
    def __init__(self, db: Session):
        self.db = db

    def render_monitored_stores(self, user_id: int) -> Dict[str, Any]:
        """Renders competitor store list with live ad signals and catalog change status"""
        stores = self.db.query(StoreModel).all()

        store_cards = []
        for s in stores:
            store_cards.append({
                "store_id": s.id,
                "domain": s.domain,
                "platform": s.platform,
                "niche": s.niche or "General",
                "monitoring_active": True,
                "ad_spy_link": f"https://www.facebook.com/ads/library/?q={s.domain}",
                "quick_actions": {
                    "view_catalog": f"/competitors/{s.id}/products",
                    "price_history": f"/competitors/{s.id}/price-history"
                }
            })

        return {
            "monitored_stores_count": len(store_cards),
            "stores": store_cards
        }