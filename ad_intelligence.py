import re
from typing import Dict, Any, List

class AdIntelligenceEngine:
    def __init__(self):
        pass

    def extract_hook_and_cta(self, ad_copy: str) -> Dict[str, str]:
        """Extracts primary hook (first sentence) and call-to-action signals"""
        if not ad_copy:
            return {"hook": "", "cta_signal": "UNKNOWN"}

        sentences = re.split(r'(?<=[.!?]) +|\n+', ad_copy.strip())
        hook = sentences[0] if sentences else ad_copy[:100]

        cta_keywords = ["shop now", "buy today", "get 50% off", "claim yours", "order now", "limited stock"]
        detected_cta = "GENERIC_PROMO"
        
        for cta in cta_keywords:
            if cta in ad_copy.lower():
                detected_cta = cta.upper()
                break

        return {
            "hook": hook,
            "cta_signal": detected_cta
        }

    def analyze_ad_creative_momentum(
        self, 
        ad_copy: str, 
        active_days: int, 
        is_active: bool
    ) -> Dict[str, Any]:
        """Calculates creative duration, fatigue level, and winning status"""
        
        hook_meta = self.extract_hook_and_cta(ad_copy)
        
        # Winning Ad Rule: Active for > 14 days usually signifies high ROI / scaled budget
        is_winning = active_days >= 14 and is_active
        
        if active_days > 45:
            creative_fatigue = "HIGH_FATIGUE_RISK"
        elif active_days >= 14:
            creative_fatigue = "SCALING_PEAK"
        else:
            creative_fatigue = "TESTING_PHASE"

        return {
            "hook": hook_meta["hook"],
            "cta": hook_meta["cta_signal"],
            "active_days": active_days,
            "is_winning_creative": is_winning,
            "creative_lifecycle_stage": creative_fatigue,
            "ad_length_type": "SHORT_FORM" if len(ad_copy) < 150 else "LONG_FORM_STORY"
        }