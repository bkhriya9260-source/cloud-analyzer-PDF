from difflib import SequenceMatcher
from typing import Dict, Any, List

class ProductMatchingEngine:
    def __init__(self):
        pass

    def calculate_string_similarity(self, title_a: str, title_b: str) -> float:
        """Calculates textual similarity ratio between two product titles"""
        return SequenceMatcher(None, title_a.lower(), title_b.lower()).ratio()

    def match_products(
        self, 
        base_product: Dict[str, Any], 
        candidate_products: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identifies identical and similar products across different stores"""
        
        base_title = base_product.get("title", "")
        base_price = base_product.get("price", 0.0)

        matches = []
        for candidate in candidate_products:
            cand_title = candidate.get("title", "")
            cand_price = candidate.get("price", 0.0)

            title_sim = self.calculate_string_similarity(base_title, cand_title)
            
            # Price delta check (Identical products usually fall in a similar price window)
            price_delta = abs(base_price - cand_price)
            price_match = price_delta <= (base_price * 0.25) if base_price > 0 else False

            # Match Score Formula (80% Title Match + 20% Price Band Match)
            match_confidence = round((title_sim * 0.80 + (0.20 if price_match else 0.0)) * 100, 1)

            if match_confidence >= 60.0:
                matches.append({
                    "matched_store": candidate.get("store_domain", "Unknown"),
                    "candidate_title": cand_title,
                    "candidate_url": candidate.get("product_url"),
                    "candidate_price": cand_price,
                    "confidence_score": match_confidence,
                    "match_type": "EXACT_SAME_PRODUCT" if match_confidence >= 85.0 else "SIMILAR_ALTERNATIVE"
                })

        return sorted(matches, key=lambda x: x["confidence_score"], reverse=True)