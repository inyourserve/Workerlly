from fastapi import APIRouter
from app.db.models.database import db
from bson import ObjectId

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
