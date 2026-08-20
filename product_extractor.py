import json
import httpx
from bs4 import BeautifulSoup
from typing import Dict, Any, List

class ProductExtractor:
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0"}

    async def extract_shopify_products(self, domain: str, limit: int = 30) -> List[Dict[str, Any]]:
        clean_domain = domain.replace("https://", "").replace("http://", "").strip("/")
        endpoint = f"https://{clean_domain}/products.json?limit={limit}"
        
        extracted_products = []
        async with httpx.AsyncClient(timeout=15) as client:
            try:
                res = await client.get(endpoint, headers=self.headers)
                if res.status_code == 200:
                    data = res.json()
                    for p in data.get("products", []):
                        variants = p.get("variants", [])
                        price = float(variants[0].get("price", 0.0)) if variants else 0.0
                        available = any(v.get("available", False) for v in variants)
                        
                        images = [img.get("src") for img in p.get("images", [])]
                        
                        extracted_products.append({
                            "id": p.get("id"),
                            "title": p.get("title"),
                            "handle": p.get("handle"),
                            "product_url": f"https://{clean_domain}/products/{p.get('handle')}",
                            "price": price,
                            "available": available,
                            "variants_count": len(variants),
                            "images": images,
                            "tags": p.get("tags", []),
                            "description": BeautifulSoup(p.get("body_html", ""), "html.parser").get_text(strip=True)
                        })
            except Exception as e:
                print(f"[ProductExtractor Error] Failed extracting {domain}: {e}")
                
        return extracted_products