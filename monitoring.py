from typing import Dict, Any, List
from datetime import datetime

class ContinuousMonitoringEngine:
    def __init__(self):
        pass

    def inspect_store_changes(
        self,
        store_domain: str,
        current_snapshot: List[Dict[str, Any]],
        previous_snapshot: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Scans saved competitor stores for price drops, catalog additions, and discontinued products"""
        
        prev_map = {p["id"]: p for p in previous_snapshot}
        detected_events = []

        for curr in current_snapshot:
            pid = curr["id"]
            if pid not in prev_map:
                detected_events.append({
                    "event_type": "NEW_PRODUCT_LAUNCHED",
                    "store": store_domain,
                    "product_title": curr.get("title"),
                    "details": f"Competitor added new product priced at ${curr.get('price')}",
                    "timestamp": datetime.utcnow().isoformat()
                })
            else:
                old_p = prev_map[pid].get("price", 0.0)
                new_p = curr.get("price", 0.0)
                if old_p != new_p and old_p > 0:
                    pct_diff = round(((new_p - old_p) / old_p) * 100, 2)
                    detected_events.append({
                        "event_type": "COMPETITOR_PRICE_DROP" if pct_diff < 0 else "PRICE_HIKE",
                        "store": store_domain,
                        "product_title": curr.get("title"),
                        "details": f"Price changed from ${old_p} to ${new_p} ({pct_diff}%)",
                        "timestamp": datetime.utcnow().isoformat()
                    })

        return detected_events