import re
from typing import Dict, Any
from scraper import CoreScraper

class StoreDiscovery:
    def __init__(self):
        self.scraper = CoreScraper()

    async def identify_platform_and_niche(self, domain: str) -> Dict[str, Any]:
        clean_domain = domain.replace("https://", "").replace("http://", "").strip("/")
        target_url = f"https://{clean_domain}"
        
        info = await self.scraper.get_basic_info(target_url)
        if info.get("status") == "failed":
            return {"domain": clean_domain, "discovered": False, "reason": "Unreachable"}

        # Platform Identification
        platform = "Custom/Other"
        if info.get("has_shopify_signal"):
            platform = "Shopify"
        elif info.get("has_woocommerce_signal"):
            platform = "WooCommerce"

        # Basic Niche Detection Engine via Title & Description keywords
        text_corpus = f"{info.get('title', '')} {info.get('description', '')}".lower()
        niche = "General E-Commerce"
        
        niche_keywords = {
            "Fashion & Apparel": ["clothing", "wear", "apparel", "shirts", "fashion", "jewelry"],
            "Home & Kitchen": ["decor", "kitchen", "furniture", "living", "home"],
            "Electronics & Gadgets": ["tech", "gadget", "charger", "audio", "electronics"],
            "Beauty & Cosmetics": ["skincare", "beauty", "makeup", "cosmetics", "glow"],
            "Pet Supplies": ["dog", "cat", "pet", "paw", "animal"]
        }

        for category, keywords in niche_keywords.items():
            if any(kw in text_corpus for kw in keywords):
                niche = category
                break

        return {
            "domain": clean_domain,
            "discovered": True,
            "platform": platform,
            "niche": niche,
            "store_title": info.get("title")
        }-