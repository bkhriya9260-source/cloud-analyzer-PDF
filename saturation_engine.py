from typing import Dict, Any

class SaturationEngine:
    def __init__(self):
        pass

    def calculate_saturation_index(
        self, 
        seller_count: int, 
        active_ad_count: int, 
        marketplace_listing_count: int
    ) -> Dict[str, Any]:
        """
        Calculates 0-100 Saturation Score based on market density:
        - 0 to 30: Low Saturation (High Opportunity Gap)
        - 31 to 70: Moderate Saturation
        - 71 to 100: Highly Saturated
        """
        
        # Weighted metric scoring
        seller_score = min(seller_count * 5, 40)             # Max 40 pts
        ad_density_score = min(active_ad_count * 4, 40)      # Max 40 pts
        marketplace_score = min(marketplace_listing_count * 2, 20) # Max 20 pts

        saturation_score = seller_score + ad_density_score + marketplace_score

        if saturation_score <= 30:
            level = "LOW"
            opportunity_gap = "LARGE_UNTAPPED_GAP"
        elif saturation_score <= 70:
            level = "MEDIUM"
            opportunity_gap = "COMPETITIVE_BUT_VIABLE"
        else:
            level = "HIGH"
            opportunity_gap = "HEAVILY_SATURATED"

        return {
            "saturation_score": saturation_score,
            "competition_level": level,
            "opportunity_gap": opportunity_gap,
            "metrics": {
                "active_sellers": seller_count,
                "running_ads_count": active_ad_count,
                "multi_marketplace_presence": marketplace_listing_count
            }
        }