from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from app.api.v1.schemas.status import StatusUpdateRequest
from app.db.models.database import db
from app.api.v1.endpoints.users import get_current_user
from app.utils.roles import role_required

router = APIRouter()


@router.post("/status", dependencies=[Depends(role_required("seeker"))])
def update_status(
    request: StatusUpdateRequest, current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    db.users.update_one(
        {"_id": ObjectId(user_id)}, {"$set": {"status": request.status}}
    )
    status_str = "online" if request.status else "offline"
    return {"message": f"Status updated to {status_str}"}


@router.get("/status", dependencies=[Depends(role_required("seeker"))])
def get_status(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    user = db.users.find_one({"_id": ObjectId(user_id)}, {"status": 1, "_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": user.get("status", False)}
