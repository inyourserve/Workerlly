from http.client import HTTPException

from fastapi import APIRouter
from app.db.models.database import db
from bson import ObjectId
from app.api.v1.schemas.city_check import CityCheckResponse

router = APIRouter()


@router.get("/categories")
def get_categories():
    categories = list(db.categories.find({}))
    # Convert ObjectId to string for each category and sub-category
    for category in categories:
        category["_id"] = str(category["_id"])
        if "sub_categories" in category:
            for sub_category in category["sub_categories"]:
                if isinstance(sub_category, dict):
                    sub_category["id"] = str(sub_category["id"])
    return {"categories": categories}


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
