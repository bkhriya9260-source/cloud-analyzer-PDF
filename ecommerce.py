import json
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def analyze_ecommerce(html: str, url: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    
    # Platform Detection
    platform = "Unknown / Custom E-commerce"
    html_str = html.lower()
    
    if "cdn.shopify.com" in html_str or "window.shopify" in html_str:
        platform = "Shopify"
    elif "woocommerce" in html_str or "wp-content/plugins/woocommerce" in html_str:
        platform = "WooCommerce"
    elif "magento" in html_str or "mage/" in html_str:
        platform = "Magento"
    elif "bigcommerce" in html_str:
        platform = "BigCommerce"
    elif "amazon." in url:
        platform = "Amazon Marketplace"

    # Schema.org / JSON-LD Data Extraction (For Product Details)
    product_data = {
        "name": None,
        "brand": None,
        "price": None,
        "currency": None,
        "availability": "Unknown",
        "sku": None,
        "description": None,
        "images": []
    }

    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        try:
            if not script.string:
                continue
            data = json.loads(script.string)
            
            if isinstance(data, list):
                data = data[0] if len(data) > 0 else {}
                
            if isinstance(data, dict) and data.get("@type") == "Product":
                product_data["name"] = data.get("name")
                product_data["description"] = data.get("description")
                product_data["sku"] = str(data.get("sku")) if data.get("sku") else None
                
                brand = data.get("brand")
                if isinstance(brand, dict):
                    product_data["brand"] = brand.get("name")
                elif isinstance(brand, str):
                    product_data["brand"] = brand
                
                offers = data.get("offers")
                if isinstance(offers, list) and len(offers) > 0:
                    offers = offers[0]
                
                if isinstance(offers, dict):
                    product_data["price"] = offers.get("price")
                    product_data["currency"] = offers.get("priceCurrency")
                    avail = offers.get("availability", "")
                    if "InStock" in avail:
                        product_data["availability"] = "In Stock"
                    elif "OutOfStock" in avail:
                        product_data["availability"] = "Out of Stock"
                        
                images = data.get("image")
                if isinstance(images, str):
                    product_data["images"].append(images)
                elif isinstance(images, list):
                    product_data["images"].extend([img for img in images if isinstance(img, str)])
                break
        except Exception:
            continue

    # Fallback Meta Parsing
    if not product_data["name"]:
        og_title = soup.find("meta", property="og:title")
        product_data["name"] = og_title["content"] if og_title else (soup.title.string if soup.title else None)

    if not product_data["price"]:
        price_meta = soup.find("meta", property="product:price:amount") or soup.find("meta", property="og:price:amount")
        if price_meta:
            product_data["price"] = price_meta.get("content")

    if not product_data["currency"]:
        curr_meta = soup.find("meta", property="product:price:currency") or soup.find("meta", property="og:price:currency")
        if curr_meta:
            product_data["currency"] = curr_meta.get("content")

    return {
        "is_ecommerce": platform != "Unknown / Custom E-commerce" or product_data["price"] is not None,
        "platform": platform,
        "product_data": product_data
    }