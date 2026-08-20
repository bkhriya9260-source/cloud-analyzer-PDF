from typing import Dict, Any, List
from sqlalchemy.orm import Session
from database import Store, Product

class CompetitorEngine:
    def __init__(self, db: Session):
        self.db = db

    def compare_catalog_snapshots(
        self,
        store_id: int,
        previous_products: List[Dict[str, Any]],
        current_products: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Detects new product launches, removed products, and price changes"""
        
        prev_map = {p["handle"]: p for p in previous_products}
        curr_map = {p["handle"]: p for p in current_products}

        new_products = []
        removed_products = []
        price_changes = []

        # Find New Products and Price Changes
        for handle, item in curr_map.items():
            if handle not in prev_map:
                new_products.append(item)
            else:
                old_price = prev_map[handle].get("price", 0.0)
                new_price = item.get("price", 0.0)
                if old_price != new_price:
                    price_changes.append({
                        "title": item.get("title"),
                        "handle": handle,
                        "old_price": old_price,
                        "new_price": new_price,
                        "diff": round(new_price - old_price, 2)
                    })

        # Find Removed Products
        for handle, item in prev_map.items():
            if handle not in curr_map:
                removed_products.append(item)

        return {
            "store_id": store_id,
            "total_current_catalog": len(current_products),
            "new_products_launched": new_products,
            "removed_products_count": len(removed_products),
            "price_adjustments": price_changes
        }

    def get_competitor_tech_signals(self, html_content: str) -> Dict[str, Any]:
        """Extracts technology stack signals (Klaviyo, Loox, Judge.me, Meta Pixel)"""
        detected_tech = []
        
        tech_signatures = {
            "Klaviyo Email Marketing": "klaviyo",
            "Judge.me Reviews": "judgeme",
            "Loox Reviews": "loox",
            "Meta Pixel": "connect.facebook.net",
            "TikTok Pixel": "analytics.tiktok.com",
            "Hotjar Analytics": "static.hotjar.com"
        }

        for tech_name, signature in tech_signatures.items():
            if signature in html_content:
                detected_tech.append(tech_name)

        return {
            "tech_stack_detected": detected_tech,
            "total_apps_count": len(detected_tech)
        }