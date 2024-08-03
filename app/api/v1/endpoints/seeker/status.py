from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends

from app.api.v1.endpoints.users import get_current_user
from app.db.models.database import db
from app.utils.roles import role_required

router = APIRouter()


@router.post("/status", dependencies=[Depends(role_required("seeker"))])
def update_status(status: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    if status not in ["online", "offline"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    db.users.update_one(
        {"_id": ObjectId(user_id)}, {"$set": {"status": status}}
    )
    return {"message": f"Status updated to {status}"}
