from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from product_search import ProductSearchEngine
from ai_engine import calculate_opportunity_score

class ProductUIController:
    def __init__(self, db: Session):
        self.db = db

    def render_search_results(
        self, 
        query: str, 
        min_price: Optional[float] = None, 
        max_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """Executes search and formats cards with Opportunity Scores & Profit Margins"""
        search_engine = ProductSearchEngine(self.db)
        raw_results = search_engine.search_products(query=query, min_price=min_price, max_price=max_price)

        formatted_cards = []
        for p in raw_results:
            selling_price = p.get("price", 0.0)
            cogs = p.get("cogs", 0.0)
            margin_pct = p.get("margin_percentage", 0.0)

            # Compute Opportunity Signal for UI Card
            score_meta = calculate_opportunity_score(
                demand_rank=2, 
                saturation_index=30, 
                margin_pct=margin_pct, 
                active_ads_count=6
            )

            formatted_cards.append({
                "product_id": p.get("product_id"),
                "title": p.get("title"),
                "selling_price": f"${selling_price}",
                "margin": f"{margin_pct}%",
                "opportunity_score": score_meta["opportunity_score"],
                "verdict_badge": score_meta["ai_verdict"],
                "store_domain": p.get("store_domain"),
                "action_links": {
                    "view_details": f"/products/{p.get('product_id')}",
                    "compare": f"/products/compare?id={p.get('product_id')}"
                }
            })

        return {
            "query_applied": query,
            "total_found": len(formatted_cards),
            "products": formatted_cards
        }