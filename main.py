import ipaddress
from urllib.parse import urlparse
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
import os
from config import settings
from database import init_db, get_db, Store, Product
from auth import router as auth_router
from subscriptions import router as sub_router
from api import router as api_router 
from product_extractor import ProductExtractor
from product_search import ProductSearchEngine
from ai_reports import AIReportEngine
from store_discovery import StoreDiscovery
from profit_engine import ProfitEngine
from trend_engine import TrendEngine
from price_intelligence import PriceIntelligenceEngine
from competitor_engine import CompetitorEngine
from saturation_engine import SaturationEngine
from opportunity_score import OpportunityScoreEngine


def validate_target_url(url: str):
    parsed = urlparse(url)
    if parsed.scheme not in ["http", "https"]:
        raise HTTPException(status_code=400, detail="Invalid URL scheme. Only http/https supported.")
    
    hostname = parsed.hostname
    if not hostname:
        raise HTTPException(status_code=400, detail="Invalid hostname.")
        
    if hostname.lower() in ["localhost", "127.0.0.1", "0.0.0.0", "::1"]:
        raise HTTPException(status_code=400, detail="Access to internal/localhost is blocked.")
        
    try:
        ip = ipaddress.ip_address(hostname)
        if ip.is_private or ip.is_loopback or ip.is_link_local:
            raise HTTPException(status_code=400, detail="Private/Internal IP address blocked.")
    except ValueError:
        pass
    return True


app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs"
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Database Schema
init_db()

# Register Core Routers
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(sub_router, prefix=settings.API_V1_PREFIX)
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def root():
    return {
        "message": "E-Commerce Intelligence Core Engine Online",
        "documentation": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "architecture": "FastAPI Async Core Engine"}


@app.post("/analyze")
async def analyze_store(data: dict, db: Session = Depends(get_db)):
    url = data.get("url", "")

    if not url:
        return {"error": "URL parameter missing"}

    # Security Validation Check
    validate_target_url(url)

    search_engine = ProductSearchEngine()
    discovery = StoreDiscovery()
    extractor = ProductExtractor()
    extracted_products = await extractor.extract_shopify_products(url)
    discovery_res = await discovery.identify_platform_and_niche(url)
    results = search_engine.search_products(url) 
    
    report_engine = AIReportEngine()
    report = report_engine.generate_executive_report(
        product_title=results.get("title", "Analyzed Store"),
        opportunity_data={"score": 85},
        profit_data={"revenue": 12500},
        saturation_data={"competition": "LOW"},
        ad_data={"winning": True},
        price_data={"price": 29.99}
    )
    
    # Database Save Logic
    store = db.query(Store).filter(Store.domain == url).first()
    if not store:
        store = Store(
            domain=url,
            platform=discovery_res.get("platform"),
            niche=discovery_res.get("niche")
        )
        db.add(store)
        db.commit()
        db.refresh(store)
        
    if extracted_products:
        for p in extracted_products:
            existing_prod = db.query(Product).filter(Product.url == p.get("url"), Product.store_id == store.id).first()
            if not existing_prod:
                new_prod = Product(
                    store_id=store.id,
                    title=p.get("title", "Unknown Product"),
                    url=p.get("url", ""),
                    image_url=p.get("image_url", ""),
                    selling_price=float(p.get("price", 0.0) or 0.0)
                )
                db.add(new_prod)
                db.commit()

    return {
        "status": "success",
        "url": url,
        "platform": discovery_res.get("platform", "Custom/Other"),
        "niche": discovery_res.get("niche", "General E-Commerce"),
        "search_data": results,
        "ai_report": report,
        "extracted_products": extracted_products
    }


@app.post("/calculate-profit")
async def calculate_profit(data: dict):
    engine = ProfitEngine()
    result = engine.calculate_unit_economics(
        selling_price=float(data.get("selling_price", 0.0)),
        supplier_cost=float(data.get("supplier_cost", 0.0)),
        shipping_cost=float(data.get("shipping_cost", 0.0)),
        estimated_ad_cpa=float(data.get("estimated_ad_cpa", 0.0))
    )
    return result  


@app.get("/analyze-trend/{product_id}")
async def analyze_product_trend(product_id: int, db: Session = Depends(get_db)):
    engine = TrendEngine(db=db)
    return engine.analyze_product_momentum(product_id=product_id)


@app.get("/price-intelligence/{product_id}")
async def get_price_intelligence(product_id: int, db: Session = Depends(get_db)):
    engine = PriceIntelligenceEngine(db=db)
    return engine.analyze_market_pricing(product_id=product_id)


@app.get("/competitor-analysis/{store_id}")
async def get_competitor_analysis(store_id: int, db: Session = Depends(get_db)):
    engine = CompetitorEngine(db=db)
    return engine.analyze_competitor(store_id=store_id)


@app.get("/saturation-analysis/{product_id}")
async def get_saturation_analysis(product_id: int, db: Session = Depends(get_db)):
    engine = SaturationEngine(db=db)
    return engine.analyze_saturation(product_id=product_id)


@app.get("/opportunity-score/{product_id}")
async def get_opportunity_score(product_id: int, db: Session = Depends(get_db)):
    engine = OpportunityScoreEngine()
    return engine.calculate_score(product_id=product_id)


@app.post("/search-products")
async def search_products(data: dict, db: Session = Depends(get_db)):
    engine = ProductSearchEngine(db=db)
    results = engine.search_products(
        query=data.get("query"),
        min_price=data.get("min_price"),
        max_price=data.get("max_price"),
        category=data.get("category"),
        min_margin=data.get("min_margin"),
        limit=data.get("limit", 20)
    )
    return {"status": "success", "results": results}


# Serve UI Dashboard directly at root "/"
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Cloud Web Analyzer - SaaS Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-950 text-white font-sans antialiased min-h-screen flex flex-col items-center justify-center p-6">
        <div class="max-w-xl w-full bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl text-center">
            <h1 class="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500 mb-3">
                Cloud Web Analyzer 🚀
            </h1>
            <p class="text-slate-400 mb-6 text-sm">
                Multi-Page SaaS Auditor Engine & Intelligence Core is live and running.
            </p>
            <div class="space-y-4 text-left">
                <div>
                    <label class="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Target Store URL</label>
                    <input type="text" id="targetUrl" placeholder="https://example.com" class="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-3 text-sm text-white focus:outline-none focus:border-cyan-500">
                </div>
                <button onclick="runAudit()" class="w-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold py-3 rounded-lg shadow-lg transition duration-200">
                    Launch Comprehensive Analysis ⚡
                </button>
            </div>
            <div id="resultBox" class="mt-6 hidden text-left bg-slate-950 p-4 rounded-lg border border-slate-800 text-xs font-mono text-cyan-300 overflow-x-auto"></div>
        </div>

        <script>
            async function runAudit() {
                const url = document.getElementById('targetUrl').value;
                const resultBox = document.getElementById('resultBox');
                if(!url) { alert('Please enter a URL'); return; }
                
                resultBox.classList.remove('hidden');
                resultBox.innerHTML = "Analyzing target store data...";
                
                try {
                    const response = await fetch('/analyze', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ url: url })
                    });
                    const data = await response.json();
                    resultBox.innerHTML = JSON.stringify(data, null, 2);
                } catch(err) {
                    resultBox.innerHTML = "Error: " + err.message;
                }
            }
        </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
