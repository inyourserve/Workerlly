from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.db.models.database import db
from bson import ObjectId
import shutil
import os
from app.api.v1.schemas.category import CategoryCreate, SubcategoryCreate

router = APIRouter()

UPLOAD_DIR = "static/uploads/cat"


@router.post("/categories")
async def create_category(
    name: str = Form(...),
    thumbnail: UploadFile = File(...),
):
    thumbnail_path = os.path.join(UPLOAD_DIR, thumbnail.filename)
    with open(thumbnail_path, "wb") as buffer:
        shutil.copyfileobj(thumbnail.file, buffer)

    category = {"name": name, "thumbnail": thumbnail_path, "sub_categories": []}
    result = db.categories.insert_one(category)
    return {"id": str(result.inserted_id), "message": "Category created successfully"}


@router.post("/subcategories")
async def create_subcategory(
    category_id: str = Form(...),
    name: str = Form(...),
    thumbnail: UploadFile = File(...),
):
    thumbnail_path = os.path.join(UPLOAD_DIR, thumbnail.filename)
    with open(thumbnail_path, "wb") as buffer:
        shutil.copyfileobj(thumbnail.file, buffer)

    subcategory = {"id": str(ObjectId()), "name": name, "thumbnail": thumbnail_path}
    db.categories.update_one(
        {"_id": ObjectId(category_id)}, {"$push": {"sub_categories": subcategory}}
    )
    return {"message": "Subcategory created successfully"}


@router.get("/categories")
async def get_categories():
    categories = list(db.categories.find({}))
    for category in categories:
        category["_id"] = str(category["_id"])
        for sub_category in category.get("sub_categories", []):
            sub_category["id"] = str(sub_category["id"])
    return {"categories": categories}
