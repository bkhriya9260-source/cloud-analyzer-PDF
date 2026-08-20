import asyncio
import httpx
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional

class CoreScraper:
    def __init__(self, concurrency_limit: int = 5, timeout: int = 15):
        self.semaphore = asyncio.Semaphore(concurrency_limit)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }
        self.timeout = timeout

    async def fetch_page(self, url: str) -> Optional[str]:
        async with self.semaphore:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                try:
                    response = await client.get(url, headers=self.headers)
                    if response.status_code == 200:
                        return response.text
                except Exception as e:
                    print(f"[Scraper Error] Failed to fetch {url}: {str(e)}")
                return None

    async def get_basic_info(self, url: str) -> Dict[str, Any]:
        html = await self.fetch_page(url)
        if not html:
            return {"status": "failed", "url": url}

        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.string.strip() if soup.title else ""
        meta_desc = soup.find("meta", {"name": "description"})
        description = meta_desc["content"].strip() if meta_desc and "content" in meta_desc.attrs else ""

        return {
            "status": "success",
            "url": url,
            "title": title,
            "description": description,
            "has_shopify_signal": "myshopify" in html or "Shopify.theme" in html,
            "has_woocommerce_signal": "woocommerce" in html or "wp-content" in html
        }

    async def crawl_queue(self, url_list: List[str]) -> List[Dict[str, Any]]:
        tasks = [self.get_basic_info(url) for url in url_list]
        return await asyncio.gather(*tasks)