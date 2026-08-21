import ipaddress
from urllib.parse import urlparse
from fastapi import HTTPException
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from database import init_db
from auth import router as auth_router
from subscriptions import router as sub_router
from api import router as api_router 
from product_search import ProductSearchEngine
from ai_reports import AIReportEngine
from store_discovery import StoreDiscovery
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
async def analyze_store(data: dict):
  url = data.get("url", "")

  if not url:
      return {"error": "URL parameter missing"}

  # Security Validation Check
  validate_target_url(url)

  search_engine = ProductSearchEngine()
  discovery = StoreDiscovery()
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
return {
        "status": "success",
        "url": url,
        "platform": discovery_res.get("platform", "Custom/Other"),
        "niche": discovery_res.get("niche", "General E-Commerce"),
        "search_data": results,
        "ai_report": report
    }
    
   
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
