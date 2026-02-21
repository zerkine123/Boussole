# ============================================
# Boussole - Financial Feasibility Service
# ============================================

"""
Financial Feasibility Engine.
Provides calculators for Landed Cost, Break-even Analysis, ROI, and Cash Flow Projections.
Integrates with Market Intelligence to provide benchmarks (e.g., avg rent).
"""

import logging
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import numpy_financial as npf

logger = logging.getLogger(__name__)

class OptimizationResult(BaseModel):
    is_feasible: bool
    break_even_months: float
    roi_3yr: float
    net_margin_percent: float
    message: str

class FinancialService:
    def __init__(self):
        pass

    def calculate_landed_cost(
        self, 
        base_price: float, 
        freight: float, 
        insurance: float, 
        customs_duty_percent: float, 
        vat_percent: float = 19.0
    ) -> Dict[str, float]:
        """
        Calculate Landed Cost for imported goods.
        Formula: (CIF + Duty) * (1 + VAT)
        """
        cif = base_price + freight + insurance
        duty_amount = cif * (customs_duty_percent / 100)
        landed_pre_vat = cif + duty_amount
        vat_amount = landed_pre_vat * (vat_percent / 100)
        total_landed = landed_pre_vat + vat_amount
        
        return {
            "base_cif": round(cif, 2),
            "duty_amount": round(duty_amount, 2),
            "vat_amount": round(vat_amount, 2),
            "total_landed_cost": round(total_landed, 2),
            "effective_tax_rate": round(((total_landed - base_price) / base_price) * 100, 1) if base_price > 0 else 0
        }

    def simulate_cash_flow(
        self,
        initial_investment: float,
        monthly_fixed_costs: float,
        unit_cost: float,
        unit_price: float,
        daily_sales_year1: int,
        growth_rate_annual: float = 0.10, # 10% YoY
        years: int = 3
    ) -> Dict[str, Any]:
        """
        Generate a 3-year monthly cash flow projection.
        """
        monthly_data = []
        cumulative_cash_flow = -initial_investment
        break_even_month = None
        
        margin_per_unit = unit_price - unit_cost
        
        current_daily_sales = daily_sales_year1
        
        for year in range(1, years + 1):
            if year > 1:
                current_daily_sales *= (1 + growth_rate_annual)
                
            monthly_sales = current_daily_sales * 30 # Approx
            
            for month in range(1, 13):
                global_month = (year - 1) * 12 + month
                
                revenue = monthly_sales * unit_price
                cogs = monthly_sales * unit_cost
                gross_profit = revenue - cogs
                net_profit = gross_profit - monthly_fixed_costs
                
                # Taxes (IBS 26% approx or TAP? Simplified for MVP)
                # Assuming 26% IBS on positive profit
                tax = max(0, net_profit * 0.26) 
                net_income = net_profit - tax
                
                cumulative_cash_flow += net_income
                
                if break_even_month is None and cumulative_cash_flow >= 0:
                    break_even_month = global_month
                
                monthly_data.append({
                    "month": global_month,
                    "year": year,
                    "revenue": round(revenue),
                    "expenses": round(cogs + monthly_fixed_costs + tax),
                    "net_income": round(net_income),
                    "balance": round(cumulative_cash_flow)
                })

        roi = ((cumulative_cash_flow + initial_investment) / initial_investment) * 100 if initial_investment else 0
        total_revenue = sum(m["revenue"] for m in monthly_data)
        total_profit = sum(m["net_income"] for m in monthly_data)
        net_margin = (total_profit / total_revenue * 100) if total_revenue else 0

        return {
            "projection": monthly_data,
            "metrics": {
                "initial_investment": initial_investment,
                "total_profit_3yr": round(total_profit),
                "roi_percent": round(roi, 1),
                "break_even_month": break_even_month or "Not reached",
                "net_margin_percent": round(net_margin, 1)
            }
        }
