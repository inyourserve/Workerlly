from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.api.v1.endpoints.users import get_current_user
from app.api.v1.schemas.user import ProfileComplete
from app.db.models.database import db
from app.utils.roles import role_required

router = APIRouter()


@router.post(
    "/profile/complete",
    dependencies=[Depends(role_required("seeker"))],
)
def complete_profile(
    profile: ProfileComplete,
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]

    # Validate category ID
    category = db.categories.find_one({"_id": ObjectId(profile.category_id)})
    if not category:
        raise HTTPException(status_code=400, detail="Invalid category ID")

    # Validate sub-category IDs
    for sub_category_id in profile.sub_category_id:
        if not any(sub["id"] == sub_category_id for sub in category["sub_categories"]):
            raise HTTPException(
                status_code=400, detail=f"Invalid sub-category ID: {sub_category_id}"
            )

    # Validate city ID
    city = db.cities.find_one({"_id": ObjectId(profile.city_id)})
    if not city:
        raise HTTPException(status_code=400, detail="Invalid city ID")

    # Update profile with IDs
    profile_data = profile.dict()
    profile_data["category_id"] = ObjectId(profile.category_id)
    profile_data["sub_category_id"] = [ObjectId(id) for id in profile.sub_category_id]
    profile_data["city_id"] = ObjectId(profile.city_id)

    db.users.update_one({"_id": ObjectId(user_id)}, {"$set": profile_data})

    return {"message": "Profile updated successfully"}
