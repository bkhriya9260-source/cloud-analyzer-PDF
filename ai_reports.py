from typing import Dict, Any

class AIReportEngine:
    def __init__(self):
        pass

    def generate_executive_report(
        self,
        product_title: str,
        opportunity_data: Dict[str, Any],
        profit_data: Dict[str, Any],
        saturation_data: Dict[str, Any],
        ad_data: Dict[str, Any],
        price_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generates comprehensive 1-click executive intelligence reports with final AI Verdict"""
        
        score = opportunity_data.get("overall_opportunity_score", 0)
        
        if score >= 80:
            verdict = "🟢 TEST"
            recommendation = "High winning potential. Low saturation with solid gross margin. Launch testing campaign immediately."
        elif score >= 55:
            verdict = "🟡 WATCH"
            recommendation = "Moderate opportunity. Monitor competitor ad volume and wait for supplier cost drops before scaling."
        else:
            verdict = "🔴 AVOID"
            recommendation = "High market saturation or razor-thin gross margins. High risk of negative ROAS."

        return {
            "report_header": {
                "product_name": product_title,
                "ai_verdict": verdict,
                "overall_opportunity_score": f"{score}/100",
                "recommendation": recommendation
            },
            "financial_breakdown": {
                "selling_price": f"${profit_data.get('selling_price', 0.0)}",
                "total_cogs": f"${profit_data.get('total_base_cogs', 0.0)}",
                "gross_margin": f"{profit_data.get('gross_margin_pct', 0.0)}%",
                "break_even_ad_cpa": f"${profit_data.get('break_even_ad_cpa', 0.0)}"
            },
            "market_and_competition": {
                "saturation_level": saturation_data.get("competition_level", "UNKNOWN"),
                "opportunity_gap": saturation_data.get("opportunity_gap", "UNKNOWN"),
                "market_average_price": f"${price_data.get('market_average_price', 0.0)}"
            },
            "ad_intelligence": {
                "active_creative_lifecycle": ad_data.get("creative_lifecycle_stage", "UNKNOWN"),
                "winning_creative_detected": ad_data.get("is_winning_creative", False),
                "primary_hook": ad_data.get("hook", "N/A")
            },
            "risk_assessment": [
                "Supplier shipping delay risk" if profit_data.get("shipping_cost", 0) > 10 else "Low shipping complexity",
                "Ad fatigue risk due to long-running competitor creatives" if ad_data.get("creative_lifecycle_stage") == "HIGH_FATIGUE_RISK" else "Fresh creative angle viable"
            ]
        }
