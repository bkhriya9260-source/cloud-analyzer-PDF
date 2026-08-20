from typing import Dict, Any, List
import datetime

class AdDataCollector:
    def __init__(self):
        pass

    def build_meta_ad_query(self, brand_name: str) -> Dict[str, Any]:
        """Constructs Ad Library intelligence query and fallback payload"""
        encoded_brand = brand_name.replace(" ", "%20")
        meta_url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&q={encoded_brand}"
        
        return {
            "source": "Meta Ad Library",
            "advertiser": brand_name,
            "ad_library_url": meta_url,
            "tracking_status": "Active Surveillance"
        }

    def process_raw_ad_creative(self, raw_ad_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Processes and structures ad copy, CTAs, and duration metadata"""
        return {
            "ad_id": raw_ad_payload.get("ad_id"),
            "advertiser": raw_ad_payload.get("page_name"),
            "ad_copy": raw_ad_payload.get("ad_copy", "").strip(),
            "cta": raw_ad_payload.get("cta_text", "SHOP_NOW"),
            "associated_product": raw_ad_payload.get("product_title"),
            "first_seen": raw_ad_payload.get("first_seen", datetime.date.today().isoformat()),
            "last_seen": raw_ad_payload.get("last_seen", datetime.date.today().isoformat()),
            "is_active": raw_ad_payload.get("is_active", True)
        }