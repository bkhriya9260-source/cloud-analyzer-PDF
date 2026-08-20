from typing import List, Dict, Any
import statistics

class PriceIntelligenceEngine:
    def __init__(self):
        pass

    def analyze_market_pricing(self, price_list: List[float]) -> Dict[str, Any]:
        """Calculates market average, min/max bounds, price spread, and discount alerts"""
        valid_prices = [p for p in price_list if p > 0]

        if not valid_prices:
            return {"error": "No valid pricing data available"}

        lowest = min(valid_prices)
        highest = max(valid_prices)
        avg_price = round(statistics.mean(valid_prices), 2)
        median_price = round(statistics.median(valid_prices), 2)

        return {
            "lowest_market_price": lowest,
            "highest_market_price": highest,
            "market_average_price": avg_price,
            "market_median_price": median_price,
            "total_competitors_analyzed": len(valid_prices),
            "recommended_sweet_spot_price": round(avg_price * 0.95, 2)
        }

    def detect_price_changes(self, old_price: float, new_price: float) -> Dict[str, Any]:
        """Detects discounts or price hikes"""
        if old_price <= 0:
            return {"type": "NO_CHANGE", "percentage": 0.0}

        diff = new_price - old_price
        pct_change = round((diff / old_price) * 100, 2)

        if pct_change < 0:
            event_type = "PROMOTION_OR_PRICE_DROP"
        elif pct_change > 0:
            event_type = "PRICE_HIKE"
        else:
            event_type = "STABLE"

        return {
            "type": event_type,
            "percentage_change": abs(pct_change),
            "old_price": old_price,
            "new_price": new_price
        }