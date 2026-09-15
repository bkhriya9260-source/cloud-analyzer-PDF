
from typing import Dict, Any
from sqlalchemy.orm import Session
from database import Product, PriceHistory


class PriceIntelligenceEngine:
    def __init__(self, db: Session):
        self.db = db

    def analyze_market_pricing(self, product_id: int) -> Dict[str, Any]:
        """
        Reads one product's saved price history and reports
        its latest price and change from the previous recorded price.
        """

        product = (
            self.db.query(Product)
            .filter(Product.id == product_id)
            .first()
        )

        if not product:
            return {
                "status": "error",
                "message": f"Product with ID {product_id} was not found."
            }

        history = (
            self.db.query(PriceHistory)
            .filter(PriceHistory.product_id == product_id)
            .order_by(PriceHistory.recorded_at.asc(), PriceHistory.id.asc())
            .all()
        )

        # Include the product's current saved price if it is not
        # already the latest recorded price.
        prices = []

        for item in history:
            try:
                price = float(item.price)
                if price > 0:
                    prices.append({
                        "price": price,
                        "recorded_at": item.recorded_at.isoformat()
                        if item.recorded_at else None
                    })
            except (TypeError, ValueError):
                continue

        try:
            current_price = float(product.selling_price)
        except (TypeError, ValueError):
            current_price = 0.0

        if current_price > 0:
            latest_history_price = prices[-1]["price"] if prices else None

            if latest_history_price != current_price:
                prices.append({
                    "price": current_price,
                    "recorded_at": None,
                    "source": "current_product_price"
                })

        if not prices:
            return {
                "status": "no_data",
                "product_id": product_id,
                "message": "No valid price history or current price is available.",
                "price_history": []
            }

        latest = prices[-1]
        previous = prices[-2] if len(prices) >= 2 else None

        if previous:
            old_price = previous["price"]
            new_price = latest["price"]
            difference = round(new_price - old_price, 2)
            percentage = round((difference / old_price) * 100, 2)

            if difference < 0:
                change_type = "PRICE_DROP"
            elif difference > 0:
                change_type = "PRICE_HIKE"
            else:
                change_type = "STABLE"
        else:
            old_price = None
            new_price = latest["price"]
            difference = None
            percentage = None
            change_type = "NOT_ENOUGH_HISTORY"

        return {
            "status": "success",
            "product_id": product_id,
            "product_title": product.title,
            "current_price": latest["price"],
            "previous_price": old_price,
            "price_difference": difference,
            "percentage_change": percentage,
            "change_type": change_type,
            "history_count": len(prices),
            "price_history": prices
        }
