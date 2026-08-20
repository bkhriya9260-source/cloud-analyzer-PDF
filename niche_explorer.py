from typing import Dict, Any, List

class NicheExplorerEngine:
    def __init__(self):
        pass

    def analyze_niche_health(
        self, 
        niche_name: str, 
        top_products: List[Dict[str, Any]], 
        avg_opportunity_score: float
    ) -> Dict[str, Any]:
        """Provides category-level market dynamics, growth potential, and risks"""
        
        total_products = len(top_products)
        high_profit_count = sum(1 for p in top_products if p.get("margin_pct", 0) >= 60.0)

        if avg_opportunity_score >= 75:
            market_verdict = "HIGH_GROWTH_HOT_NICHE"
        elif avg_opportunity_score >= 50:
            market_verdict = "STABLE_COMPETITIVE_NICHE"
        else:
            market_verdict = "SATURATED_LOW_MARGIN_NICHE"

        return {
            "niche_category": niche_name,
            "overall_niche_health_score": round(avg_opportunity_score, 1),
            "market_verdict": market_verdict,
            "category_stats": {
                "total_monitored_products": total_products,
                "high_margin_products_pct": round((high_profit_count / total_products) * 100, 1) if total_products > 0 else 0.0
            },
            "recommended_entry_strategy": (
                "🎯 High margins and strong demand signals. Ideal for launching new branded storefronts."
                if avg_opportunity_score >= 75
                else "⚠️ Enter only with unique product differentiators or superior ad creatives."
            )
        }