from typing import Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import PriceHistory, Product

class TrendEngine:
    def __init__(self, db: Session):
        self.db = db

    def analyze_product_momentum(self, product_id: int) -> Dict[str, Any]:
        """Calculates demand trajectory, momentum score, and historical price stability"""
        snapshots = (
            self.db.query(PriceHistory)
            .filter(PriceHistory.product_id == product_id)
            .order_by(PriceHistory.recorded_at.asc())
            .all()
        )

        if not snapshots:
            return {
                "momentum_signal": "EMERGING",
                "trend_status": "NEUTRAL",
                "price_change_pct": 0.0,
                "historical_data_points": 0
            }

        first_price = snapshots[0].price
        latest_price = snapshots[-1].price
        price_diff = latest_price - first_price
        pct_change = round((price_diff / first_price) * 100, 2) if first_price > 0 else 0

        # Signal Trajectory Logic
        if pct_change < -5.0:
            signal = "PRICE_DROP_DEMAND_BOOST"
            trend = "RISING"
        elif len(snapshots) >= 5:
            signal = "HIGH_MOMENTUM_BESTSELLER"
            trend = "STRONG_RISING"
        else:
            signal = "EMERGING_PRODUCT"
            trend = "EMERGING"

        return {
            "product_id": product_id,
            "trend_status": trend,
            "momentum_signal": signal,
            "historical_price_change_pct": pct_change,
            "total_scan_history": len(snapshots),
            "first_seen_price": first_price,
            "current_price": latest_price
        }