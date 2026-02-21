from fastapi import APIRouter, Depends, HTTPException
from typing import Any

from app.services.financial_service import FinancialService
from app.schemas.finance import (
    LandedCostRequest, 
    LandedCostResponse, 
    SimulationRequest, 
    SimulationResponse
)

router = APIRouter()

@router.post("/landed-cost", response_model=LandedCostResponse)
def calculate_landed_cost(request: LandedCostRequest) -> Any:
    """
    Calculate landed cost including duties and VAT.
    """
    service = FinancialService()
    result = service.calculate_landed_cost(
        base_price=request.base_price,
        freight=request.freight,
        insurance=request.insurance,
        customs_duty_percent=request.customs_duty_percent,
        vat_percent=request.vat_percent
    )
    return result

@router.post("/simulate", response_model=SimulationResponse)
def simulate_cash_flow(request: SimulationRequest) -> Any:
    """
    Generate 3-year cash flow projection based on investment and operational costs.
    """
    service = FinancialService()
    result = service.simulate_cash_flow(
        initial_investment=request.initial_investment,
        monthly_fixed_costs=request.monthly_fixed_costs,
        unit_cost=request.unit_cost,
        unit_price=request.unit_price,
        daily_sales_year1=request.daily_sales,
        growth_rate_annual=request.growth_rate_annual,
        years=request.years
    )
    return result
