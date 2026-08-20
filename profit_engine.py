from typing import Dict, Any

class ProfitEngine:
    def __init__(self):
        pass

    def calculate_unit_economics(
        self,
        selling_price: float,
        supplier_cost: float,
        shipping_cost: float = 0.0,
        platform_fee_pct: float = 2.9,     # e.g., Shopify Payments / Stripe
        fixed_transaction_fee: float = 0.30,
        estimated_ad_cpa: float = 0.0      # Cost per Acquisition
    ) -> Dict[str, Any]:
        """Calculates Gross Margin, Net Profit, ROI, and Break-Even Ad CPA"""
        
        if selling_price <= 0:
            return {"error": "Selling price must be greater than zero"}

        platform_fee = (selling_price * (platform_fee_pct / 100.0)) + fixed_transaction_fee
        total_cogs = supplier_cost + shipping_cost
        gross_profit = selling_price - total_cogs - platform_fee
        gross_margin_pct = (gross_profit / selling_price) * 100.0

        net_profit = gross_profit - estimated_ad_cpa
        net_margin_pct = (net_profit / selling_price) * 100.0
        
        roi_pct = (gross_profit / total_cogs) * 100.0 if total_cogs > 0 else 0.0
        break_even_cpa = gross_profit  # Maximum allowable ad cost before loss

        return {
            "selling_price": round(selling_price, 2),
            "supplier_cost": round(supplier_cost, 2),
            "shipping_cost": round(shipping_cost, 2),
            "platform_fees": round(platform_fee, 2),
            "total_base_cogs": round(total_cogs, 2),
            "gross_profit": round(gross_profit, 2),
            "gross_margin_pct": round(gross_margin_pct, 2),
            "net_profit": round(net_profit, 2),
            "net_margin_pct": round(net_margin_pct, 2),
            "roi_pct": round(roi_pct, 2),
            "break_even_ad_cpa": round(break_even_cpa, 2)
        }