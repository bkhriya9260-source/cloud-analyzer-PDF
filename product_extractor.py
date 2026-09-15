
import logging
from typing import Any, Dict, List
from urllib.parse import urlparse, urlunparse

import httpx
from bs4 import BeautifulSoup

from security import validate_url


logger = logging.getLogger(__name__)

DEFAULT_LIMIT = 30
MAX_LIMIT = 100
REQUEST_TIMEOUT = 15.0


class ProductExtractor:
    def __init__(self, timeout: float = REQUEST_TIMEOUT):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (compatible; StoreAnalyzer/1.0)",
            "Accept": "application/json,text/plain,*/*",
        }

    @staticmethod
    def _normalize_store_url(domain: str) -> str:
        """
        Normalize a store domain into an HTTPS origin.
        Examples:
            example.com       -> https://example.com
            https://example.com/path -> https://example.com
        """
        if not isinstance(domain, str) or not domain.strip():
            raise ValueError("A valid store domain or URL is required.")

        raw = domain.strip()

        if "://" not in raw:
            raw = f"https://{raw}"

        parsed = urlparse(raw)

        if parsed.scheme.lower() not in {"http", "https"}:
            raise ValueError("Only HTTP and HTTPS store URLs are supported.")

        if not parsed.hostname:
            raise ValueError("The store URL must include a hostname.")

        # Remove any supplied path, query, or fragment. The Shopify endpoint
        # is built from the store origin only.
        netloc = parsed.netloc
        origin = urlunparse(
            (
                parsed.scheme.lower(),
                netloc,
                "",
                "",
                "",
                "",
            )
        )

        return validate_url(origin)

    async def extract_shopify_products(
        self,
        domain: str,
        limit: int = DEFAULT_LIMIT,
    ) -> List[Dict[str, Any]]:
        """
        Extract publicly available Shopify products from /products.json.

        Returns an empty list when the endpoint is unavailable, inaccessible,
        or does not contain a valid Shopify products response.
        """
        try:
            safe_origin = self._normalize_store_url(domain)
        except (ValueError, httpx.HTTPError, Exception) as exc:
            logger.warning("Invalid store URL %r: %s", domain, exc)
            return []

        try:
            requested_limit = int(limit)
        except (TypeError, ValueError):
            requested_limit = DEFAULT_LIMIT

        requested_limit = max(1, min(requested_limit, MAX_LIMIT))
        endpoint = f"{safe_origin.rstrip('/')}/products.json"

        params = {"limit": requested_limit}
        extracted_products: List[Dict[str, Any]] = []

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=False,
                headers=self.headers,
            ) as client:
                response = await client.get(endpoint, params=params)

            if response.status_code != 200:
                logger.info(
                    "Shopify product endpoint returned HTTP %s for %s",
                    response.status_code,
                    safe_origin,
                )
                return []

            try:
                data = response.json()
            except ValueError:
                logger.info(
                    "Shopify product endpoint returned invalid JSON for %s",
                    safe_origin,
                )
                return []

            products = data.get("products") if isinstance(data, dict) else None
            if not isinstance(products, list):
                logger.info(
                    "Shopify product endpoint did not return a products list for %s",
                    safe_origin,
                )
                return []

            for product in products[:requested_limit]:
                if not isinstance(product, dict):
                    continue

                variants = product.get("variants") or []
                if not isinstance(variants, list):
                    variants = []

                first_variant = variants[0] if variants else {}
                if not isinstance(first_variant, dict):
                    first_variant = {}

                try:
                    price = float(first_variant.get("price") or 0.0)
                except (TypeError, ValueError):
                    price = 0.0

                available = any(
                    isinstance(variant, dict)
                    and bool(variant.get("available", False))
                    for variant in variants
                )

                handle = product.get("handle")
                product_url = (
                    f"{safe_origin.rstrip('/')}/products/{handle}"
                    if isinstance(handle, str) and handle
                    else None
                )

                raw_images = product.get("images") or []
                images = []

                if isinstance(raw_images, list):
                    for image in raw_images:
                        if not isinstance(image, dict):
                            continue
                        image_src = image.get("src")
                        if isinstance(image_src, str) and image_src.strip():
                            images.append(image_src.strip())

                body_html = product.get("body_html") or ""
                description = BeautifulSoup(
                    body_html if isinstance(body_html, str) else "",
                    "html.parser",
                ).get_text(" ", strip=True)

                tags = product.get("tags") or []
                if isinstance(tags, str):
                    tags = [tag.strip() for tag in tags.split(",") if tag.strip()]
                elif not isinstance(tags, list):
                    tags = []

                image_url = images[0] if images else None

                extracted_products.append(
                    {
                        "id": product.get("id"),
                        "title": product.get("title") or "",
                        "handle": handle,
                        "product_url": product_url,
                        "url": product_url,
                        "price": price,
                        "available": available,
                        "variants_count": len(variants),
                        "images": images,
                        "image_url": image_url,
                        "tags": tags,
                        "description": description,
                    }
                )

        except httpx.TimeoutException:
            logger.warning("Timed out extracting products from %s", safe_origin)
        except httpx.HTTPError as exc:
            logger.warning(
                "HTTP error extracting products from %s: %s",
                safe_origin,
                exc,
            )
        except Exception:
            logger.exception(
                "Unexpected error extracting products from %s",
                safe_origin,
            )

        return extracted_products
