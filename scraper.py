
import asyncio
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from fastapi import HTTPException

from security import validate_url


class CoreScraper:
    def __init__(
        self,
        concurrency_limit: int = 5,
        timeout: int = 15,
        max_response_bytes: int = 2_000_000,
        max_redirects: int = 5,
        retries: int = 2,
    ):
        self.semaphore = asyncio.Semaphore(max(1, concurrency_limit))
        self.timeout = max(1, timeout)
        self.max_response_bytes = max(1024, max_response_bytes)
        self.max_redirects = max(0, max_redirects)
        self.retries = max(0, retries)

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,"
                "application/xml;q=0.9,*/*;q=0.8"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }

    async def _request_with_validated_redirects(
        self,
        client: httpx.AsyncClient,
        url: str,
    ) -> Optional[str]:
        """
        Request a page while validating every redirect target.

        Automatic redirects are disabled so that each new destination
        can be checked before the next request is made.
        """
        current_url = validate_url(url)

        for redirect_count in range(self.max_redirects + 1):
            response = await client.get(
                current_url,
                headers=self.headers,
                follow_redirects=False,
            )

            if response.is_redirect:
                if redirect_count >= self.max_redirects:
                    return None

                location = response.headers.get("location")
                if not location:
                    return None

                next_url = urljoin(current_url, location)
                current_url = validate_url(next_url)
                continue

            if response.status_code != 200:
                return None

            content_length = response.headers.get("content-length")
            if content_length:
                try:
                    if int(content_length) > self.max_response_bytes:
                        return None
                except ValueError:
                    pass

            content = response.content
            if len(content) > self.max_response_bytes:
                return None

            encoding = response.encoding or "utf-8"
            return content.decode(encoding, errors="replace")

        return None

    async def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch HTML safely. Returns None for expected fetch failures.
        Invalid or unsafe URLs raise HTTPException from validate_url().
        """
        validate_url(url)

        timeout = httpx.Timeout(self.timeout)
        limits = httpx.Limits(
            max_connections=max(1, self.semaphore._value),
            max_keepalive_connections=max(1, self.semaphore._value),
        )

        async with self.semaphore:
            try:
                async with httpx.AsyncClient(
                    timeout=timeout,
                    limits=limits,
                    follow_redirects=False,
                ) as client:
                    for attempt in range(self.retries + 1):
                        try:
                            return await self._request_with_validated_redirects(
                                client,
                                url,
                            )
                        except HTTPException:
                            # Unsafe redirect destinations must not be retried.
                            raise
                        except (
                            httpx.TimeoutException,
                            httpx.NetworkError,
                            httpx.RemoteProtocolError,
                        ):
                            if attempt >= self.retries:
                                return None

                            await asyncio.sleep(min(0.5 * (2**attempt), 2.0))
                        except httpx.HTTPError:
                            return None

            except HTTPException:
                raise
            except Exception:
                # Keep scraper failures from crashing a whole crawl.
                return None

        return None

    async def get_basic_info(self, url: str) -> Dict[str, Any]:
        html = await self.fetch_page(url)

        if not html:
            return {
                "status": "failed",
                "url": url,
                "title": "",
                "description": "",
                "has_shopify_signal": False,
                "has_woocommerce_signal": False,
            }

        soup = BeautifulSoup(html, "html.parser")

        title = ""
        if soup.title:
            title = soup.title.get_text(" ", strip=True)

        meta_desc = soup.find("meta", attrs={"name": "description"})
        description = ""
        if meta_desc:
            description = str(meta_desc.get("content", "")).strip()

        html_lower = html.lower()

        return {
            "status": "success",
            "url": url,
            "title": title,
            "description": description,
            "has_shopify_signal": (
                "myshopify" in html_lower
                or "shopify.theme" in html_lower
                or "cdn.shopify.com" in html_lower
            ),
            "has_woocommerce_signal": (
                "woocommerce" in html_lower
                or "wp-content" in html_lower
            ),
        }

    async def crawl_queue(
        self,
        url_list: List[str],
    ) -> List[Dict[str, Any]]:
        """
        Crawl a list of URLs while respecting the concurrency semaphore.
        Invalid URLs return an individual failed result instead of
        cancelling the entire batch.
        """
        async def crawl_one(url: str) -> Dict[str, Any]:
            try:
                return await self.get_basic_info(url)
            except HTTPException as exc:
                return {
                    "status": "failed",
                    "url": url,
                    "error": exc.detail,
                }

        tasks = [crawl_one(url) for url in url_list]
        return await asyncio.gather(*tasks)
