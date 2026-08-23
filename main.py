from product_extractor import ProductExtractor
import ipaddress
from urllib.parse import urlparse
from fastapi import HTTPException, Depends
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from database import init_db, get_db, Store, Product
from sqlalchemy.orm import Session
from auth import router as auth_router
from subscriptions import router as sub_router
from api import router as api_router 
from product_search import ProductSearchEngine
from ai_reports import AIReportEngine
from store_discovery import StoreDiscovery
from profit_engine import ProfitEngine
from trend_engine import TrendEngine
from price_intelligence import PriceIntelligence
from competitor_engine import CompetitorEngine
from saturation_engine import SaturationEngine
from opportunity_score import OpportunityEngine
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
    engine = PriceIntelligence(db=db)
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
    engine = OpportunityEngine(db=db)
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
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
