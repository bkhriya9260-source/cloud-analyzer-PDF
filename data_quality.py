import hashlib
import time
from typing import Dict, Any, Tuple

class DataQualityAnalyzer:
    def __init__(self, stale_threshold_seconds: int = 86400 * 7):
        self.stale_threshold = stale_threshold_seconds

    def generate_fingerprint(self, record: Dict[str, Any]) -> str:
        unique_str = f"{record.get('domain', '')}-{record.get('title', '')}".lower()
        return hashlib.md5(unique_str.encode('utf-8')).hexdigest()

    def evaluate_quality(self, record: Dict[str, Any]) -> Tuple[float, Dict[str, bool]]:
        checks = {
            "missing_title": not bool(record.get("title")),
            "missing_price": record.get("price") is None,
            "invalid_price": (record.get("price") or 0) <= 0 or (record.get("price") or 0) > 100000,
            "is_stale": (time.time() - record.get("updated_at", 0)) > self.stale_threshold
        }

        score = 100.0
        if checks["missing_title"]: score -= 40.0
        if checks["missing_price"]: score -= 40.0
        if checks["invalid_price"]: score -= 30.0
        if checks["is_stale"]: score -= 20.0

        final_score = max(0.0, score)
        return final_score, checks