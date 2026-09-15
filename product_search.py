
import logging
import re
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from database import Product, Store


logger = logging.getLogger(__name__)

DEFAULT_LIMIT = 20
MAX_LIMIT = 100


class ProductSearchEngine:
    def __init__(self, db: Session):
        self.db = db

    def parse_natural_language_query(self, query: str) -> Dict[str, Any]:
        """
        Parse simple queries such as:
        - Find products under $80
        - Find products between $20 and $80
        - Find low-competition products

        Note: low_competition is parsed as intent only. It is not applied
        unless the database has a confirmed competition-score field.
        """
        query_lower = (query or "").lower()

        filters: Dict[str, Any] = {
            "max_price": None,
            "min_price": None,
            "category": None,
            "low_competition": False,
        }

        # Match a range first so "20-80" is not interpreted as "under 80".
        price_range = re.search(
            r"\$?\s*(\d+(?:\.\d{1,2})?)\s*(?:-|to)\s*\$?\s*(\d+(?:\.\d{1,2})?)",
            query_lower,
        )

        if price_range:
            first = float(price_range.group(1))
            second = float(price_range.group(2))
            filters["min_price"] = min(first, second)
            filters["max_price"] = max(first, second)
        else:
            under_match = re.search(
                r"\b(?:under|below|less than|up to)\s+\$?\s*(\d+(?:\.\d{1,2})?)",
                query_lower,
            )
            if under_match:
                filters["max_price"] = float(under_match.group(1))

            over_match = re.search(
                r"\b(?:over|above|more than|at least)\s+\$?\s*(\d+(?:\.\d{1,2})?)",
                query_lower,
            )
            if over_match:
                filters["min_price"] = float(over_match.group(1))

        if "low competition" in query_lower or "low-competition" in query_lower:
            filters["low_competition"] = True

        return filters

    def search_products(
        self,
        query: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        category: Optional[str] = None,
        min_margin: Optional[float] = None,
        country: str = "US",
        limit: int = DEFAULT_LIMIT,
    ) -> List[Dict[str, Any]]:
        """
        Search products stored in the database.

        `country` is retained for API compatibility, but is not applied
        because the current Product/Store schema has not been confirmed to
        contain a country field.
        """
        if query:
            parsed = self.parse_natural_language_query(query)

            if max_price is None:
                max_price = parsed["max_price"]
            if min_price is None:
                min_price = parsed["min_price"]

        try:
            limit = int(limit)
        except (TypeError, ValueError):
            limit = DEFAULT_LIMIT

        limit = max(1, min(limit, MAX_LIMIT))

        db_query = self.db.query(Product).join(Store)

        if min_price is not None:
            db_query = db_query.filter(Product.selling_price >= min_price)

        if max_price is not None:
            db_query = db_query.filter(Product.selling_price <= max_price)

        if category:
            db_query = db_query.filter(Store.niche == category)

        try:
            products = db_query.limit(limit).all()
        except Exception:
            logger.exception("Database product search failed")
            raise

        results: List[Dict[str, Any]] = []

        for product in products:
            try:
                selling_price = float(product.selling_price or 0)
                cogs = float(product.cogs or 0)
            except (TypeError, ValueError):
                logger.warning(
                    "Skipping product %r due to invalid price or COGS",
                    getattr(product, "id", None),
                )
                continue

            margin = (
                round(((selling_price - cogs) / selling_price) * 100, 2)
                if selling_price > 0
                else 0.0
            )

            if min_margin is not None and margin < min_margin:
                continue

            store = getattr(product, "store", None)

            results.append(
                {
                    "product_id": product.id,
                    "title": product.title,
                    "url": product.url,
                    "price": selling_price,
                    "cogs": cogs,
                    "margin_percentage": margin,
                    "store_domain": store.domain if store else "Unknown",
                    "is_best_seller": bool(
                        getattr(product, "is_best_seller", False)
                    ),
                }
            )

        return results
