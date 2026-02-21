from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class LandedCostRequest(BaseModel):
    base_price: float = Field(..., description="Base price (FOB) in DZD or converted currency")
    freight: float = Field(0, description="Freight cost")
    insurance: float = Field(0, description="Insurance cost")
    customs_duty_percent: float = Field(30, description="Customs duty rate (e.g., 30 for 30%)")
    vat_percent: float = Field(19, description="VAT rate (default 19%)")

class LandedCostResponse(BaseModel):
    base_cif: float
    duty_amount: float
    vat_amount: float
    total_landed_cost: float
    effective_tax_rate: float

class SimulationRequest(BaseModel):
    initial_investment: float
    monthly_fixed_costs: float
    unit_cost: float
    unit_price: float
    daily_sales: int = Field(..., description="Projected daily sales in Year 1")
    growth_rate_annual: float = Field(0.10, description="Annual growth rate (0.10 for 10%)")
    years: int = Field(3, description="Projection period in years")

class CashFlowMonth(BaseModel):
    month: int
    year: int
    revenue: float
    expenses: float
    net_income: float
    balance: float

class SimulationMetrics(BaseModel):
    initial_investment: float
    total_profit_3yr: float
    roi_percent: float
    break_even_month: object # int or str
    net_margin_percent: float

class SimulationResponse(BaseModel):
    projection: List[CashFlowMonth]
    metrics: SimulationMetrics
