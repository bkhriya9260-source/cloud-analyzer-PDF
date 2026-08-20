from typing import Dict, Any

class OpportunityScoreEngine:
    def __init__(self):
        pass

    def calculate_score(
        self,
        demand_score: int,      # 0 to 100
        trend_score: int,       # 0 to 100
        competition_score: int, # 0 to 100 (Higher means lower competition)
        saturation_score: int,  # 0 to 100 (Higher means more saturated)
        profit_score: int,      # 0 to 100
        ad_activity_score: int  # 0 to 100
    ) -> Dict[str, Any]:
        """
        Calculates a weighted composite Opportunity Score (0 - 100).
        Weights: Demand (25%), Profit (25%), Trend (20%), Ad Momentum (15%), Saturation Penalty (15%)
        """
        
        # Saturation is inverted: High saturation reduces the total score
        saturation_penalty = (100 - saturation_score) * 0.15
        
        weighted_score = (
            (demand_score * 0.25) +
            (profit_score * 0.25) +
            (trend_score * 0.20) +
            (ad_activity_score * 0.15) +
            saturation_penalty
        )

        final_score = int(round(min(max(weighted_score, 0), 100)))

        # Signal Indicator & Verdict Output
        if final_score >= 85:
            badge = "🟢 Strong Opportunity"
            verdict = "TEST_IMMEDIATELY"
        elif final_score >= 65:
            badge = "🟡 Moderate Opportunity"
            verdict = "WATCH_CLOSELY"
        else:
            badge = "🔴 High Risk / Saturated"
            verdict = "AVOID"

        return {
            "overall_opportunity_score": final_score,
            "badge": badge,
            "verdict": verdict,
            "breakdown": {
                "demand_score": demand_score,
                "trend_score": trend_score,
                "competition_score": competition_score,
                "saturation_index": saturation_score,
                "profit_score": profit_score,
                "ad_momentum_score": ad_activity_score
            }
        }