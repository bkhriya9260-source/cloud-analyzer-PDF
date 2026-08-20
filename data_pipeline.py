import re
from typing import Dict, Any, Optional

class DataPipeline:
    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text).strip()

    def normalize_price(self, raw_price: Any) -> Optional[float]:
        if raw_price is None:
            return None
        clean_p = re.sub(r'[^\d.]', '', str(raw_price))
        try:
            return float(clean_p)
        except ValueError:
            return None

    def validate_raw(self, raw_data: Dict[str, Any]) -> bool:
        required_fields = ["title", "price", "url"]
        return all(k in raw_data and raw_data[k] for k in required_fields)

    def process_record(self, raw_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self.validate_raw(raw_data):
            return None

        cleaned_title = self.clean_text(raw_data.get("title", ""))
        normalized_price = self.normalize_price(raw_data.get("price"))

        if normalized_price is None or normalized_price <= 0:
            return None

        db_record = {
            "title": cleaned_title,
            "price": normalized_price,
            "currency": raw_data.get("currency", "USD").upper(),
            "url": raw_data["url"].strip(),
            "domain": raw_data.get("domain", "").lower(),
            "category": self.clean_text(raw_data.get("category", "General")),
            "updated_at": int(time.time())
        }

        intelligence_record = {
            **db_record,
            "price_tier": "budget" if normalized_price < 25 else "premium",
            "search_keywords": list(set(cleaned_title.lower().split()))
        }

        return intelligence_record