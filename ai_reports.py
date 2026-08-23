from typing import Dict, Any, List

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
            recommendation = "High winning potential. Low saturation with solid gross margin. Launch video ads ASAP."
        elif score >= 55:
            verdict = "🟡 WATCH"
            recommendation = "Moderate opportunity. Monitor competitor ad volume and wait for price stability."
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
                "Ad fatigue risk due to long-running competitor creatives" if ad_data.get("creative_lifecycle_stage") == "HIGH_FATIGUE_RISK" else "Fresh creative angle gap available"
            ]
        }


class ReportGenerator:
    def __init__(self):
        pass

    def generate_comprehensive_report(self, consolidated_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates structured executive AI reports using actual signals from 
        product, trend, profit, saturation, and ad intelligence engines.
        """
        product_info = consolidated_data.get("product_info", {})
        trend_data = consolidated_data.get("trend_data", {})
        profit_data = consolidated_data.get("profit_data", {})
        competitor_data = consolidated_data.get("competitor_data", {})
        saturation_data = consolidated_data.get("saturation_data", {})
        ad_insights = consolidated_data.get("ad_insights", {})

        title = product_info.get("title", "Target Product")
        opp_score = consolidated_data.get("opportunity_score", 50)
        net_margin = profit_data.get("net_margin_percent", 0)

        exec_summary = (
            f"Analysis for '{title}' shows an overall Opportunity Score of {opp_score}/100. "
            f"Estimated Net Profit Margin is currently standing at {net_margin}%."
        )

        trend_status = trend_data.get("trend_status", "STABLE")
        opportunity_desc = (
            f"Market demand direction is {trend_status}. "
            f"Tracked ad signals show active scaling formats, indicating strong buyer interest."
        )

        strengths = []
        weaknesses = []

        if net_margin >= 30:
            strengths.append("High Profit Margin potential (>30%).")
        else:
            weaknesses.append("Tight Profit Margins (<30%), requiring strict ad-spend control.")

        if saturation_data.get("saturation_level") == "LOW":
            strengths.append("Low market saturation allows for easier ad penetration.")
        else:
            weaknesses.append("High seller competition in current ad channels.")

        risks = [
            "Ad fatigue risk if marketing creatives are not refreshed frequently.",
            "Supplier fulfillment delay during peak testing scale."
        ]

        top_ad_format = ad_insights.get("metrics", {}).get("top_performing_format", "UGC Video")
        recommended_strategy = (
            f"Focus testing on {top_ad_format} ad creatives. "
            f"Target hook angles centered around problem-solving and immediate social proof."
        )

        return {
            "status": "success",
            "report": {
                "executive_summary": exec_summary,
                "market_opportunity": opportunity_desc,
                "strengths": strengths if strengths else ["Moderate product viability."],
                "weaknesses": weaknesses if weaknesses else ["Standard competition levels."],
                "risks": risks,
                "recommended_strategy": recommended_strategy
            }
        }
