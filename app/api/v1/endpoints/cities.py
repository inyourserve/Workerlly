from http.client import HTTPException

from fastapi import APIRouter, Query
from app.db.models.database import db
from bson import ObjectId
from app.api.v1.schemas.city_check import CityCheckResponse

router = APIRouter()


@router.get("/cities")
def get_cities():
    cities = list(db.cities.find({}))
    # Convert ObjectId to string for each city
    for city in cities:
        city["_id"] = str(city["_id"])
    return {"cities": cities}


@router.patch("/cities/{city_id}")
def update_city_service_status(city_id: str, update: CityCheckResponse):
    result = db.cities.update_one(
        {"_id": ObjectId(city_id)}, {"$set": {"is_served": update.is_served}}
    )
    if result.modified_count == 1:
        return {"success": True, "message": "City service status updated successfully"}
    else:
        raise HTTPException(
            status_code=404, detail="City not found or status unchanged"
        )


@router.get("/city/check", response_model=CityCheckResponse)
async def check_city(
    city_id: str = Query(..., description="The ID of the city to check")
):
    # Check if the city is served based on the city_id and is_served field
    city_data = db.cities.find_one({"_id": ObjectId(city_id), "is_served": True})
    if city_data:
        return CityCheckResponse(is_served=True)
    else:
        return CityCheckResponse(is_served=False)
