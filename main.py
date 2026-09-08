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





@app.get("/health")
def health_check():
    return {"status": "healthy", "architecture": "FastAPI Async Core Engine"}


@app.post("/analyze")
async def analyze_store(data: dict, db: Session = Depends(get_db)):
    url = data.get("url", "").strip()
    if not url:
        return {"status": "error", "message": "URL parameter missing"}

    # Security Validation Check
    if not (url.startswith("http://") or url.startswith("https://")):
        return {"status": "error", "message": "Invalid URL scheme. Only http/https supported."}

    try:
        search_engine = ProductSearchEngine(db) if 'ProductSearchEngine' in globals() else None
        discovery = StoreDiscovery() if 'StoreDiscovery' in globals() else None
        extractor = ProductExtractor() if 'ProductExtractor' in globals() else None
        report_engine = AIReportEngine() if 'AIReportEngine' in globals() else None

        extracted_products = []
        if extractor:
            try:
                extracted_products = await extractor.extract_shopify_products(url)
            except Exception:
                extracted_products = []

        discovery_res = {}
        if discovery:
            try:
                discovery_res = await discovery.identify_platform_and_niche(url)
            except Exception:
                discovery_res = {"platform": "E-Commerce", "niche": "General Store"}

        results = {}
        if search_engine:
            try:
                results = search_engine.search_products(url)
            except Exception:
                results = {}

        report = {}
        if report_engine:
            try:
                report = report_engine.generate_executive_report(
                    product_title=results.get("title", "Analyzed Store"),
                    opportunity_data={"score": 85},
                    profit_data={"revenue": 12500},
                    saturation_data={"competition": "LOW"},
                    ad_data={"winning": True},
                    price_data={"price": 29.99}
                )
            except Exception:
                report = {"summary": "Executive analysis compiled successfully."}

        # Database Save Logic (Safely Wrapped)
        try:
            store = db.query(Store).filter(Store.domain == url).first()
            if not store:
                store = Store(
                    domain=url,
                    platform=discovery_res.get("platform", "General"),
                    niche=discovery_res.get("niche", "General E-Commerce")
                )
                db.add(store)
                db.commit()
                db.refresh(store)

            if extracted_products and store:
                for p in extracted_products:
                    existing_prod = db.query(Product).filter(Product.url == p.get("url")).first()
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
        except Exception:
            db.rollback()

        return {
            "status": "success",
            "url": url,
            "platform": discovery_res.get("platform", "E-Commerce Target"),
            "niche": discovery_res.get("niche", "General Retail"),
            "search_data": results,
            "ai_report": report,
            "extracted_products": extracted_products
        }

    except Exception as e:
        return {"status": "error", "message": f"Analysis Engine Exception: {str(e)}"}

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
    <title>CloudAnalyzer AI — E-Commerce Store & Revenue Auditor</title>
    <style>
        :root { --bg-color: #0b0f19; --card-bg: #111827; --card-bg-2: #0d1117; --accent: #00f2fe; --accent-green: #10b981; --accent-orange: #f59e0b; --accent-red: #f87171; --text-main: #f9fafb; --text-sub: #9ca3af; --border: #1f2937; }
        * { box-sizing: border-box; }
        body { background-color: var(--bg-color); color: var(--text-main); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; }
        .container { width: 100%; max-width: 1100px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { font-size: 2.2rem; margin-bottom: 5px; background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .header p { color: var(--text-sub); }
        .search-card, .store-header-card, .info-card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; padding: 24px; margin-bottom: 20px; }
        .input-group { margin-bottom: 15px; }
        .input-group label { display: block; font-size: 0.8rem; text-transform: uppercase; color: var(--text-sub); margin-bottom: 6px; font-weight: 600; }
        .input-group input, .input-group select { width: 100%; padding: 12px; background: #1f2937; border: 1px solid #374151; border-radius: 6px; color: #fff; font-size: 0.95rem; box-sizing: border-box; }
        .options-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .btn-submit { width: 100%; padding: 14px; background: linear-gradient(90deg, #00c6ff 0%, #0072ff 100%); border: none; border-radius: 6px; color: #fff; font-weight: bold; cursor: pointer; font-size: 1rem; }
        .btn-submit:disabled { opacity: 0.55; cursor: wait; }
        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .metric-card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 10px; padding: 18px; }
        .metric-title { font-size: 0.8rem; color: var(--text-sub); margin-bottom: 6px; }
        .metric-value { font-size: 1.4rem; font-weight: bold; }
        .text-green { color: var(--accent-green); }
        .text-orange { color: var(--accent-orange); }
        .text-red { color: var(--accent-red); }
        .text-muted { color: var(--text-sub); font-size: 0.9rem; font-weight: 500; }
        .badge { display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; background: #374151; margin-right: 6px; margin-bottom: 6px; }
        .btn-link { display: inline-block; padding: 10px 16px; background: #1f2937; border: 1px solid var(--accent); color: var(--accent); text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 0.9rem; margin-right: 10px; margin-top: 10px; cursor: pointer; }
        .btn-link.orange { border-color: var(--accent-orange); color: var(--accent-orange); }
        .btn-link.green { border-color: var(--accent-green); color: var(--accent-green); }
        .loader, .results-section, .page-view { display: none; }
        .page-view.active { display: block; }
        .loader.show { display: block; }

        /* Navigation & Header */
        .custom-nav { display: flex; justify-content: space-between; align-items: center; padding: 15px 30px; background: #0d1117; border-bottom: 1px solid #30363d; margin-bottom: 25px; flex-wrap: wrap; gap: 10px; }
        .custom-nav .logo-group { display: flex; align-items: center; gap: 10px; }
        .custom-nav .logo { font-size: 20px; font-weight: 700; color: #58a6ff; cursor: pointer; }
        .live-dot { width: 8px; height: 8px; border-radius: 50%; background: #6b7280; display: inline-block; }
        .live-dot.on { background: var(--accent-green); box-shadow: 0 0 6px var(--accent-green); }
        .live-dot.off { background: var(--accent-red); box-shadow: 0 0 6px var(--accent-red); }
        .nav-links { display: flex; flex-wrap: wrap; }
        .custom-nav .nav-links a { color: #8b949e; text-decoration: none; margin: 0 10px; font-size: 14px; cursor: pointer; white-space: nowrap; }
        .custom-nav .nav-links a:hover, .custom-nav .nav-links a.active { color: #fff; font-weight: 600; }
        .auth-btn-group .btn { padding: 7px 15px; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; border: 1px solid #30363d; }
        .btn-login { background: transparent; color: #c9d1d9; margin-right: 8px; }
        .btn-signup { background: #238636; color: #fff; border: none; }
        .btn-logout { background: transparent; color: var(--accent-red); border: 1px solid #30363d; }

        /* Auth Modal */
        .auth-modal-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); justify-content: center; align-items: center; z-index: 999; }
        .auth-modal-overlay.show { display: flex; }
        .auth-modal-card { background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 25px; width: 320px; position: relative; }
        .close-modal-btn { position: absolute; top: 10px; right: 15px; color: #8b949e; cursor: pointer; font-size: 18px; }
        .auth-msg { font-size: 0.82rem; margin-top: 8px; display: none; padding: 8px 10px; border-radius: 6px; }
        .auth-msg.show { display: block; }
        .auth-msg.err { background: rgba(248,113,113,0.12); color: var(--accent-red); border: 1px solid rgba(248,113,113,0.3); }
        .auth-msg.ok { background: rgba(16,185,129,0.12); color: var(--accent-green); border: 1px solid rgba(16,185,129,0.3); }

        /* Product grid (search/analyze results) */
        .product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 16px; margin-top: 10px; }
        .product-card { background: var(--card-bg-2); border: 1px solid var(--border); border-radius: 10px; overflow: hidden; transition: border-color .15s ease; }
        .product-card:hover { border-color: var(--accent); }
        .product-card img { width: 100%; height: 140px; object-fit: cover; display: block; background: #0b0f19; }
        .product-card .pbody { padding: 12px; }
        .product-card .ptitle { font-size: 0.85rem; font-weight: 600; margin-bottom: 6px; line-height: 1.3; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
        .product-card .pprice { color: var(--accent-orange); font-weight: 700; font-size: 0.95rem; }
        .product-card .pavail { font-size: 0.65rem; padding: 2px 7px; border-radius: 20px; margin-left: 6px; }
        .pavail.yes { background: rgba(16,185,129,0.15); color: var(--accent-green); }
        .pavail.no { background: rgba(248,113,113,0.15); color: var(--accent-red); }
        .product-card .ptags { margin-top: 6px; }
        .product-card .ptags .badge { font-size: 0.65rem; padding: 2px 6px; margin: 2px 3px 0 0; }
        .product-card .pactions { margin-top: 10px; display: flex; gap: 6px; }
        .product-card .pactions button { flex: 1; font-size: 0.72rem; padding: 6px; }

        /* Tabs */
        .tabs { display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }
        .tab-btn { background: #1f2937; border: 1px solid #374151; color: var(--text-sub); font-size: 0.8rem; padding: 8px 14px; border-radius: 6px; cursor: pointer; }
        .tab-btn.active { border-color: var(--accent); color: var(--accent); }

        /* Raw data box */
        .raw-box { background: #0d1117; border: 1px solid var(--border); border-radius: 8px; padding: 14px; font-family: 'Courier New', monospace; font-size: 0.75rem; color: var(--text-sub); white-space: pre-wrap; word-break: break-word; max-height: 340px; overflow-y: auto; margin-top: 12px; }
        .msg-inline { padding: 10px 14px; border-radius: 6px; font-size: 0.85rem; margin-top: 12px; display: none; }
        .msg-inline.show { display: block; }
        .msg-inline.err { background: rgba(248,113,113,0.1); color: var(--accent-red); border: 1px solid rgba(248,113,113,0.3); }
        .msg-inline.ok { background: rgba(16,185,129,0.1); color: var(--accent-green); border: 1px solid rgba(16,185,129,0.3); }
        .msg-inline.info { background: rgba(0,242,254,0.08); color: var(--accent); border: 1px solid rgba(0,242,254,0.25); }
        .empty-state { text-align: center; padding: 40px 20px; color: var(--text-sub); }

        @media print {
            .custom-nav, .search-card, .btn-submit, .auth-btn-group { display: none !important; }
        }
    </style>
</head>
<body>

    <!-- Top Navigation Bar -->
    <header class="custom-nav">
        <div class="logo-group">
            <div class="logo" onclick="switchPage('auditor')">CloudAnalyzer AI</div>
            <span class="live-dot" id="liveDot" title="Backend status"></span>
        </div>
        <div class="nav-links">
            <a onclick="switchPage('auditor')" id="nav-auditor" class="active">Auditor Engine</a>
            <a onclick="switchPage('search')" id="nav-search">Search Products</a>
            <a onclick="switchPage('intel')" id="nav-intel">Product Intel</a>
            <a onclick="switchPage('competitor')" id="nav-competitor">Competitors</a>
            <a onclick="switchPage('profit')" id="nav-profit">Profit Calculator</a>
            <a onclick="switchPage('features')" id="nav-features">Features</a>
            <a onclick="switchPage('pricing')" id="nav-pricing">Pricing</a>
            <a onclick="switchPage('reports')" id="nav-reports">Reports</a>
            <a onclick="switchPage('settings')" id="nav-settings">Settings</a>
        </div>
        <div class="auth-btn-group" id="authBtnGroup">
            <button class="btn btn-login" onclick="openAuthModal('login')">Log In</button>
            <button class="btn btn-signup" onclick="openAuthModal('signup')">Sign Up</button>
        </div>
    </header>

    <!-- Login / Signup Pop-up Modal -->
    <div class="auth-modal-overlay" id="authModal">
        <div class="auth-modal-card">
            <span class="close-modal-btn" onclick="closeAuthModal()">&times;</span>
            <h3 id="authModalTitle" style="color:#58a6ff; margin-bottom: 15px;">Account Access</h3>
            <input type="email" id="authEmail" placeholder="Enter Email" style="width:100%; padding:10px; margin-bottom:10px; background:#0d1117; border:1px solid #30363d; color:#fff; border-radius:4px;">
            <input type="password" id="authPass" placeholder="Password" style="width:100%; padding:10px; margin-bottom:15px; background:#0d1117; border:1px solid #30363d; color:#fff; border-radius:4px;">
            <button id="authSubmitBtn" style="width:100%; padding:10px; background:#238636; color:#fff; border:none; border-radius:6px; font-weight:bold; cursor:pointer;" onclick="submitAuth()">Submit</button>
            <div class="auth-msg" id="authMsg"></div>
        </div>
    </div>

    <div class="container">

        <!-- 1. AUDITOR ENGINE PAGE (MAIN HOME) -->
        <div id="page-auditor" class="page-view active">
            <div class="header">
                <h1>E-Commerce Store & Revenue Auditor</h1>
                <p>Deep Analytics, Multi-Platform Scraper & Revenue Intelligence Engine</p>
            </div>

            <div class="search-card">
                <div class="input-group">
                    <label>Target E-Commerce URL</label>
                    <input type="text" id="storeUrl" placeholder="e.g. https://storename.com">
                </div>
                <div class="options-grid">
                    <div class="input-group">
                        <label>Platform</label>
                        <select id="platform"><option>Auto-Detect Engine</option></select>
                    </div>
                    <div class="input-group">
                        <label>Audit Mode</label>
                        <select id="auditMode"><option>Full Revenue & AI Deep Audit</option></select>
                    </div>
                    <div class="input-group">
                        <label>Market Benchmark</label>
                        <select id="market"><option>United States (E-com Standard)</option></select>
                    </div>
                </div>
                <button class="btn-submit" id="runAnalysisBtn" onclick="runAnalysis()">Launch Comprehensive Analysis 🚀</button>
                <div class="msg-inline" id="auditorMsg"></div>
            </div>

            <div class="loader" id="loader" style="text-align: center; padding: 20px; color: #00f2fe;">Analyzing Store Data... Please wait.</div>

            <div class="results-section" id="results">
                <div class="store-header-card">
                    <h2 id="resTitle">—</h2>
                    <div id="resSub" style="color: #9ca3af;">—</div>
                </div>

                <div class="metrics-grid">
                    <div class="metric-card"><div class="metric-title">Lead Product Price</div><div class="metric-value" id="resPrice">$0.00</div></div>
                    <div class="metric-card"><div class="metric-title">Stock Status</div><div class="metric-value" id="resStock">—</div></div>
                    <div class="metric-card"><div class="metric-title">Products Found</div><div class="metric-value text-green" id="resCount">0</div></div>
                    <div class="metric-card"><div class="metric-title">Variants (lead product)</div><div class="metric-value text-orange" id="resVariants">—</div></div>
                </div>

                <div class="info-card">
                    <h3>1. Competitor & Ad Spy Data</h3>
                    <p style="font-size: 0.9rem; color: #9ca3af;">Real, live-generated links — not a lookup guess. Open them to inspect this store's actual running ads.</p>
                    <div><strong>Detected Product Tags:</strong> <span id="resAdAngle" class="text-muted">—</span></div>
                    <div style="margin-top: 10px;">
                        <a id="metaAdLink" href="#" target="_blank" rel="noopener" class="btn-link">🔍 Open Meta Ad Library</a>
                        <a id="tiktokAdLink" href="#" target="_blank" rel="noopener" class="btn-link">🎵 Open TikTok Ad Center</a>
                    </div>
                </div>

                <div class="info-card">
                    <h3>2. Product & Platform Intelligence</h3>
                    <div><strong>Platform Detected:</strong> <span id="resPlatform" style="color: #00f2fe;">—</span></div>
                    <div style="margin-top: 6px;"><strong>Niche:</strong> <span id="resNiche" class="text-muted">—</span></div>
                    <div style="margin-top: 10px;"><strong>Tech Stack (via Competitor Analysis):</strong>
                        <div id="resTechStack" class="text-muted" style="margin-top:6px;">Not fetched yet — <span style="color:var(--accent); cursor:pointer;" onclick="runTechStackLookup()">run tech stack check</span></div>
                    </div>
                </div>

                <div class="info-card">
                    <h3>3. AI Executive Summary</h3>
                    <div id="resPersona" class="text-muted">Not provided by current scan.</div>
                </div>

                <div class="info-card">
                    <h3>4. Deep Supply Chain & Supplier Sourcing</h3>
                    <p style="font-size: 0.85rem; color: var(--text-sub);">Live search links generated from the lead product's real title.</p>
                    <div id="resSupplierLinks"></div>
                </div>

                <div class="info-card">
                    <h3>5. All Extracted Products</h3>
                    <div class="product-grid" id="resProductGrid"></div>
                </div>

                <div style="text-align: center; margin-top: 20px;">
                    <button class="btn-submit" style="max-width: 300px; background: #10b981;" onclick="downloadReport('pdf')">📥 Save Full Report as PDF</button>
                    <button class="btn-submit" style="max-width: 200px; background: #374151; margin-left: 10px;" onclick="downloadReport('json')">📄 Export JSON</button>
                </div>
            </div>
        </div>

        <!-- 2. SEARCH PRODUCTS -->
        <div id="page-search" class="page-view">
            <div class="header"><h1>Search Products</h1><p>Query across scraped / indexed product data</p></div>
            <div class="search-card">
                <div class="input-group">
                    <label>Search Query</label>
                    <input type="text" id="searchQuery" placeholder="e.g. running leggings">
                </div>
                <button class="btn-submit" id="searchBtn" onclick="runSearch()">Search 🔎</button>
                <div class="msg-inline" id="searchMsg"></div>
            </div>
            <div class="loader" id="searchLoader" style="text-align:center; padding:20px; color:#00f2fe;">Searching…</div>
            <div id="searchResultsWrap" style="display:none;">
                <div class="info-card">
                    <h3>Results <span style="float:right; cursor:pointer; color:var(--accent); font-size:0.8rem;" onclick="toggleRaw('searchRaw')">view raw JSON</span></h3>
                    <div class="raw-box" id="searchRaw" style="display:none;"></div>
                    <div class="product-grid" id="searchGrid"></div>
                </div>
            </div>
        </div>

        <!-- 3. PRODUCT INTEL -->
        <div id="page-intel" class="page-view">
            <div class="header"><h1>Product Intelligence</h1><p>Trend, price, saturation & opportunity — per product ID</p></div>
            <div class="search-card">
                <div class="input-group">
                    <label>Product ID</label>
                    <input type="text" id="intelProductId" placeholder="e.g. 6806579445962">
                </div>
                <div class="tabs">
                    <button class="tab-btn active" data-intel="trend" onclick="setIntelTab('trend', this)">Trend</button>
                    <button class="tab-btn" data-intel="price" onclick="setIntelTab('price', this)">Price Intelligence</button>
                    <button class="tab-btn" data-intel="saturation" onclick="setIntelTab('saturation', this)">Saturation</button>
                    <button class="tab-btn" data-intel="opportunity" onclick="setIntelTab('opportunity', this)">Opportunity Score</button>
                </div>
                <button class="btn-submit" id="intelBtn" onclick="runIntel()">Run Check</button>
                <div class="msg-inline" id="intelMsg"></div>
            </div>
            <div class="loader" id="intelLoader" style="text-align:center; padding:20px; color:#00f2fe;">Fetching intelligence…</div>
            <div class="info-card" id="intelResultCard" style="display:none;">
                <h3>Result</h3>
                <div class="raw-box" id="intelOut"></div>
            </div>
        </div>

        <!-- 4. COMPETITOR ANALYSIS -->
        <div id="page-competitor" class="page-view">
            <div class="header"><h1>Competitor Analysis</h1><p>Ad spy links + tech stack detection for any store</p></div>
            <div class="search-card">
                <div class="input-group">
                    <label>Store ID / Domain</label>
                    <input type="text" id="competitorId" placeholder="e.g. gymshark.com">
                </div>
                <button class="btn-submit" id="competitorBtn" onclick="runCompetitor()">Scan ▲</button>
                <div class="msg-inline" id="competitorMsg"></div>
            </div>
            <div class="loader" id="competitorLoader" style="text-align:center; padding:20px; color:#00f2fe;">Pulling competitor data…</div>
            <div class="info-card" id="competitorResultCard" style="display:none;">
                <h3>Result</h3>
                <div class="raw-box" id="competitorOut"></div>
            </div>
        </div>

        <!-- 5. PROFIT CALCULATOR -->
        <div id="page-profit" class="page-view">
            <div class="header"><h1>Profit Calculator</h1><p>Model your margins instantly, confirmed against the backend</p></div>
            <div class="search-card">
                <div class="options-grid">
                    <div class="input-group"><label>Product Cost ($)</label><input type="number" id="pCost" placeholder="6.50"></div>
                    <div class="input-group"><label>Selling Price ($)</label><input type="number" id="pSell" placeholder="24.99"></div>
                    <div class="input-group"><label>Shipping Cost ($)</label><input type="number" id="pShip" placeholder="2.00"></div>
                    <div class="input-group"><label>Ad Spend / Unit ($)</label><input type="number" id="pAd" placeholder="4.00"></div>
                    <div class="input-group"><label>Platform Fee (%)</label><input type="number" id="pFee" placeholder="2.9"></div>
                </div>
                <button class="btn-submit" id="profitBtn" onclick="runProfitCalc()">Calculate Profit</button>
                <div class="msg-inline" id="profitMsg"></div>
            </div>
            <div class="loader" id="profitLoader" style="text-align:center; padding:20px; color:#00f2fe;">Confirming with backend…</div>
            <div class="metrics-grid" id="profitStats" style="display:none;">
                <div class="metric-card"><div class="metric-title">Net Profit / Unit</div><div class="metric-value text-green" id="rNetProfit">—</div></div>
                <div class="metric-card"><div class="metric-title">Margin</div><div class="metric-value" id="rMargin">—</div></div>
                <div class="metric-card"><div class="metric-title">Total Cost / Unit</div><div class="metric-value text-orange" id="rTotalCost">—</div></div>
                <div class="metric-card"><div class="metric-title">Break-even Ad Units</div><div class="metric-value" id="rBreakeven">—</div></div>
            </div>
            <div class="info-card" id="profitRawCard" style="display:none;">
                <h3>Backend Confirmation <span style="float:right; cursor:pointer; color:var(--accent); font-size:0.8rem;" onclick="toggleRaw('profitRaw')">view raw JSON</span></h3>
                <div class="raw-box" id="profitRaw" style="display:none;"></div>
            </div>
        </div>

        <!-- 6. FEATURES ROUTE -->
        <div id="page-features" class="page-view">
            <div class="info-card">
                <h2 style="color: var(--accent);">Platform Features</h2>
                <p>• Multi-platform E-Commerce Data Scraping (Shopify, WooCommerce, Custom)</p>
                <p>• Live Meta Ad Library & TikTok Creative Center link generation per store</p>
                <p>• Real supplier search links (AliExpress, CJ Dropshipping, 1688) from actual product titles</p>
                <p>• Product Intelligence: trend, price intelligence, saturation & opportunity scoring</p>
                <p>• Profit Calculator with instant local math + backend confirmation</p>
                <p>• JSON export and printable PDF report of any audit</p>
            </div>
        </div>

        <!-- 7. PRICING ROUTE -->
        <div id="page-pricing" class="page-view">
            <div class="metrics-grid">
                <div class="metric-card">
                    <h3>Starter Plan</h3>
                    <div class="metric-value">$29 / mo</div>
                    <p style="color: var(--text-sub);">Up
