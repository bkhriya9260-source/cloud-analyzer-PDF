from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from database import Product, Store, PriceHistory

class ProductSearchEngine:
    def __init__(self, db: Session):
        self.db = db

    def parse_natural_language_query(self, query: str) -> Dict[str, Any]:
        """
        Parses queries like 'Find me low-competition products under $80'
        into executable database parameters.
        """
        query_lower = query.lower()
        extracted_filters = {
            "max_price": None,
            "min_price": None,
            "category": None,
            "low_competition": False
        }

        # Price parsing
        import re
        price_match = re.search(r'under\s+\$?(\d+)', query_lower)
        if price_match:
            extracted_filters["max_price"] = float(price_match.group(1))

        price_between = re.search(r'\$?(\d+)\s*-\s*\$?(\d+)', query_lower)
        if price_between:
            extracted_filters["min_price"] = float(price_between.group(1))
            extracted_filters["max_price"] = float(price_between.group(2))

        if "low competition" in query_lower or "low-competition" in query_lower:
            extracted_filters["low_competition"] = True

        return extracted_filters

    def search_products(
        self,
        query: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        category: Optional[str] = None,
        min_margin: Optional[float] = None,
        country: str = "US",
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Multi-filter & Natural Language Product Discovery Engine"""
        
        # Merge natural language filters if string query provided
        if query:
            parsed = self.parse_natural_language_query(query)
            max_price = max_price or parsed.get("max_price")
            min_price = min_price or parsed.get("min_price")

        db_query = self.db.query(Product).join(Store)

        if min_price is not None:
            db_query = db_query.filter(Product.selling_price >= min_price)
        if max_price is not None:
            db_query = db_query.filter(Product.selling_price <= max_price)
        if category:
            db_query = db_query.filter(Store.niche == category)

        results = db_query.limit(limit).all()

        output = []
        for p in results:
            margin = round(((p.selling_price - p.cogs) / p.selling_price) * 100, 2) if p.selling_price > 0 else 0
            if min_margin and margin < min_margin:
                continue

            output.append({
                "product_id": p.id,
                "title": p.title,
                "url": p.url,
                "price": p.selling_price,
                "cogs": p.cogs,
                "margin_percentage": margin,
                "store_domain": p.store.domain if p.store else "Unknown",
                "is_best_seller": p.is_best_seller
            })

        return output