from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from bs4 import BeautifulSoup
import os
import json
from urllib.parse import urlparse, quote

app = FastAPI(title="Ultimate E-commerce AI & Revenue Intelligence Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    url: str

@app.get("/")
def home():
    return {
        "status": "Operational",
        "engine": "Master AI & Revenue Intelligence Engine",
        "version": "2.0-Final"
    }

@app.post("/analyze")
async def analyze(req: AnalyzeRequest, x_api_key: str = Header(None)):
    if x_api_key != "ADMIN123":
        raise HTTPException(status_code=401, detail="Unauthorized API Key")
    
    target_url = req.url.strip()
    if not target_url.startswith(("http://", "https://")):
        target_url = "https://" + target_url

    parsed_domain = urlparse(target_url).netloc

    # ==========================================
    # MODULE 1: SHOPIFY DEEP JSON SCRAPER
    # ==========================================
    shopify_data = None
    json_url = f"https://{parsed_domain}/products.json"
    
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
            res = await client.get(json_url, headers={"User-Agent": "Mozilla/5.0"})
            if res.status_code == 200:
                shopify_data = res.json()
    except Exception:
        shopify_data = None

    extracted_price = None
    product_title = "E-commerce Store Front"
    variants_count = 1
    vendor_name = parsed_domain
    
    if shopify_data and "products" in shopify_data and len(shopify_data["products"]) > 0:
        first_prod = shopify_data["products"][0]
        product_title = first_prod.get("title", product_title)
        vendor_name = first_prod.get("vendor", parsed_domain)
        variants = first_prod.get("variants", [])
        variants_count = len(variants)
        if variants:
            try:
                extracted_price = float(variants[0].get("price", 0.0))
            except Exception:
                extracted_price = None

    # ==========================================
    # MODULE 2: BEAUTIFUL SOUP FALLBACK SCRAPER
    # ==========================================
    scraped_text = ""
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
            html_res = await client.get(target_url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(html_res.text, 'html.parser')
            if product_title == "E-commerce Store Front" and soup.title:
                product_title = soup.title.string.strip()
            
            for script in soup(["script", "style", "nav", "footer"]):
                script.decompose()
            scraped_text = soup.get_text(separator=' ')[:2500]
    except Exception:
        scraped_text = f"Target Domain: {parsed_domain}"

    # ==========================================
    # MODULE 3: REVENUE & FINANCIAL CALCULATOR
    # ==========================================
    base_price = extracted_price if extracted_price and extracted_price > 0 else 29.99
    
    # Advanced Multi-Variant Sales Formula
    est_monthly_units = max(180, (variants_count * 95) + 240)
    est_monthly_revenue = round(est_monthly_units * base_price, 2)
    
    # E-commerce Benchmark Economics (3x Sourcing & Ad Rule)
    cogs = round(base_price / 3.0, 2)
    est_ad_spend = round(base_price * 0.35, 2)
    net_profit_per_unit = round(base_price - cogs - est_ad_spend, 2)
    est_monthly_profit = round(net_profit_per_unit * est_monthly_units, 2)

    # ==========================================
    # MODULE 4: COMPETITOR & SUPPLIER RESEARCH
    # ==========================================
    search_query = quote(f"{product_title} aliexpress supplier")
    supplier_search_url = f"https://www.google.com/search?q={search_query}"

    # ==========================================
    # MODULE 5: REAL GEMINI AI AUDITOR ENGINE
    # ==========================================
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    
    ai_prompt = f"""
    You are an Elite E-commerce Auditor, Dropshipping Specialist & Media Buyer.
    Analyze this store data:
    Domain: {parsed_domain}
    Product Title: {product_title}
    Retail Price: ${base_price}
    Est. Monthly Sales Volume: {est_monthly_units} units
    Extracted Web Text: {scraped_text}

    Return ONLY a valid JSON object matching this structure without code blocks or markdown:
    {{
        "description": "2-sentence clear summary of what this store or product offers.",
        "target_audience": "Exact US target buyer persona (Age, Gender, Interests, Household Income, Buying Triggers).",
        "marketing_angle": "High converting 3-second TikTok/Reels video ad hook & UGC creative strategy.",
        "weak_points": [
            "Conversion weakness 1 (UI/UX, Trust badges, or Headline)",
            "Conversion weakness 2",
            "Conversion weakness 3",
            "Conversion weakness 4"
        ]
    }}
    """

    ai_analysis = {
        "target_audience": "US Impulse Buyers (Age 18-38), Interested in Trending Tech & Problem Solvers",
        "marketing_angle": "3-Second Visual Hook: Show immediate problem -> demonstrate solution in 5 seconds -> CTA discount.",
        "weak_points": [
            "Lack of prominent social proof/reviews above the fold.",
            "Checkout CTA button lacks high-contrast visual focus.",
            "Mobile page load optimization required for ad traffic.",
            "Free shipping threshold notice is not visible enough."
        ]
    }
    ai_desc = f"Comprehensive store analysis for {parsed_domain}"

    if gemini_api_key:
        try:
            gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_api_key}"
            async with httpx.AsyncClient(timeout=18.0) as client:
                ai_res = await client.post(
                    gemini_url,
                    json={"contents": [{"parts": [{"text": ai_prompt}]}]}
                )
                res_data = ai_res.json()
                raw_text = res_data['candidates'][0]['content']['parts'][0]['text']
                clean_json = raw_text.replace("```json", "").replace("```", "").strip()
                parsed_ai = json.loads(clean_json)
                
                ai_desc = parsed_ai.get("description", ai_desc)
                ai_analysis = {
                    "target_audience": parsed_ai.get("target_audience", ai_analysis["target_audience"]),
                    "marketing_angle": parsed_ai.get("marketing_angle", ai_analysis["marketing_angle"]),
                    "weak_points": parsed_ai.get("weak_points", ai_analysis["weak_points"])
                }
        except Exception:
            pass

    # ==========================================
    # MODULE 6: COMPREHENSIVE RESPONSE PAYLOAD
    # ==========================================
    return {
        "store_info": {
            "domain": parsed_domain,
            "vendor": vendor_name,
            "product_title": product_title,
            "price": f"${base_price:.2f}",
            "variants_found": variants_count
        },
        "description": ai_desc,
        "revenue_intelligence": {
            "est_monthly_revenue": f"${est_monthly_revenue:,.2f}",
            "est_monthly_units_sold": est_monthly_units,
            "est_cogs": f"${cogs:.2f}",
            "est_ad_spend_per_unit": f"${est_ad_spend:.2f}",
            "net_profit_margin_per_unit": f"${net_profit_per_unit:.2f}",
            "est_monthly_profit": f"${est_monthly_profit:,.2f}"
        },
        "supplier_research": {
            "supplier_search_link": supplier_search_url
        },
        "ai_analysis": ai_analysis
    }
