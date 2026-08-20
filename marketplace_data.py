import httpx
from bs4 import BeautifulSoup
from typing import Dict, Any

class MarketplaceData:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    async def get_amazon_product_signal(self, keyword: str) -> Dict[str, Any]:
        encoded_kw = keyword.replace(" ", "+")
        search_url = f"https://www.amazon.com/s?k={encoded_kw}"
        
        return {
            "marketplace": "Amazon",
            "search_keyword": keyword,
            "search_url": search_url,
            "status": "Ready for Proxy Processing"
        }

    async def get_ebay_product_signal(self, keyword: str) -> Dict[str, Any]:
        encoded_kw = keyword.replace(" ", "+")
        search_url = f"https://www.ebay.com/sch/i.html?_nkw={encoded_kw}"
        
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            try:
                res = await client.get(search_url, headers=self.headers)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, "html.parser")
                    items = soup.find_all("div", {"class": "s-item__info"}, limit=5)
                    
                    extracted = []
                    for item in items:
                        title_el = item.find("div", {"class": "s-item__title"})
                        price_el = item.find("span", {"class": "s-item__price"})
                        if title_el and price_el:
                            extracted.append({
                                "title": title_el.get_text(strip=True),
                                "price": price_el.get_text(strip=True)
                            })
                    return {"marketplace": "eBay", "results": extracted}
            except Exception as e:
                print(f"[eBay Scraper Error]: {e}")
                
        return {"marketplace": "eBay", "results": []}