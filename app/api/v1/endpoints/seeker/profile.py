from bson import ObjectId
from fastapi import APIRouter, Depends

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
    db.users.update_one({"_id": ObjectId(user_id)}, {"$set": profile.dict()})
    return {"message": "Profile updated successfully"}
