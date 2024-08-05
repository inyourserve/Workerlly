from fastapi import APIRouter, HTTPException
from bson import ObjectId
from app.api.v1.schemas.salary import (
    SalaryCalculationRequest,
    SalaryCalculationResponse,
)
from app.db.models.database import db

router = APIRouter()


@router.post("/salary/calculate", response_model=SalaryCalculationResponse)
async def calculate_salary(request: SalaryCalculationRequest):
    # Fetch the rate for the given city_id and category_id
    rate_data = db.rates.find_one(
        {
            "city_id": str(request.city_id),
            "category_id": str(request.category_id),
        }
    )
    print(
        f"Rate data fetched for city_id {request.city_id} and category_id {request.category_id}: {rate_data}"
    )

    if not rate_data:
        raise HTTPException(
            status_code=404,
            detail="Rate not found for the given city and category",
        )

    rate_per_hour = rate_data["rate_per_hour"]
    hours_per_day = request.hours_per_day
    days_per_month = request.days_per_month

    # Calculate expected monthly income
    expected_monthly_income = rate_per_hour * hours_per_day * days_per_month

    return SalaryCalculationResponse(
        rate_per_hour=rate_per_hour,
        expected_monthly_income=expected_monthly_income,
    )
