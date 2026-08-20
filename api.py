from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db, User
from auth import get_current_user
from subscriptions import check_user_limit
from product_search import ProductSearchEngine
from ai_reports import AIReportEngine

router = APIRouter(prefix="/intelligence", tags=["Product Intelligence API"])

@router.get("/search")
def search_products_api(
    query: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Product Search Endpoint with Authentication & Subscription Usage Limits"""
    
    # 1. Enforce Subscription Quotas
    check_user_limit(current_user.id, action="search", db=db)
    
    # 2. Execute Intelligence Search
    search_engine = ProductSearchEngine(db=db)
    results = search_engine.search_products(query=query)
    
    return {
        "status": "success",
        "user_email": current_user.email,
        "query": query,
        "results_count": len(results),
        "data": results
    }

@router.post("/generate-report")
def generate_report_api(
    product_title: str,
    selling_price: float,
    cogs: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generates complete AI product analysis report"""
    
    report_engine = AIReportEngine()
    
    # Mock parameters passed to report generator
    mock_opp = {"overall_opportunity_score": 85}
    mock_profit = {"selling_price": selling_price, "total_base_cogs": cogs, "gross_margin_pct": round(((selling_price-cogs)/selling_price)*100, 2), "break_even_ad_cpa": round(selling_price-cogs, 2)}
    mock_sat = {"competition_level": "LOW", "opportunity_gap": "LARGE_UNTAPPED_GAP"}
    mock_ad = {"creative_lifecycle_stage": "SCALING_PEAK", "is_winning_creative": True, "hook": "Stop scrolling! Save 50% today."}
    mock_price = {"market_average_price": selling_price * 1.05}

    report = report_engine.generate_executive_report(
        product_title=product_title,
        opportunity_data=mock_opp,
        profit_data=mock_profit,
        saturation_data=mock_sat,
        ad_data=mock_ad,
        price_data=mock_price
    )
    
    return {"status": "success", "report": report}