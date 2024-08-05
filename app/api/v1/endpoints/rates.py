# app/api/v1/endpoints/rates.py
from app.db.models.database import db
from app.api.v1.schemas.rate import Rate
from fastapi import APIRouter, HTTPException
from bson import ObjectId

router = APIRouter()


@router.post("/rates")
def create_or_update_rate(rate: Rate):
    existing_rate = db.rates.find_one(
        {"city_id": rate.city_id, "category_id": rate.category_id}
    )

    if existing_rate:
        db.rates.update_one(
            {"_id": existing_rate["_id"]},
            {"$set": {"rate_per_hour": rate.rate_per_hour}},
        )
        return {"message": "Rate updated successfully"}
    else:
        db.rates.insert_one(rate.dict())
        return {"message": "Rate submitted successfully"}


@router.get("/rate/fetch")
async def fetch_rate(city_id: str, category_id: str):
    # Fetch the rate for the given city_id and category_id
    rate_data = db.rates.find_one({"city_id": city_id, "category_id": category_id})
    if not rate_data:
        raise HTTPException(
            status_code=404, detail="Rate not found for the given city and category"
        )

    return {
        "city_id": city_id,
        "category_id": category_id,
        "rate_per_hour": rate_data["rate_per_hour"],
    }


@router.get("/rates/{city_id}")
async def get_rates_for_city(city_id: str):
    rates = list(db.rates.find({"city_id": ObjectId(city_id)}))
    for rate in rates:
        rate["_id"] = str(rate["_id"])
        rate["city_id"] = str(rate["city_id"])
        rate["category_id"] = str(rate["category_id"])
    return {"rates": rates}
