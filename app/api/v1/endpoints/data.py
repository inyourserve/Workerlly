from fastapi import APIRouter

from app.db.models.database import db

router = APIRouter()


@router.get("/categories")
def get_categories():
    categories = list(db.categories.find({}, {"_id": 0}))
    return {"categories": categories}


@router.get("/cities")
def get_cities():
    cities = list(db.cities.find({}, {"_id": 0}))
    return {"cities": cities}
