from typing import List

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from app.api.v1.endpoints.users import get_current_user
from app.api.v1.schemas.job import JobRead, JobBid
from app.db.models.database import db
from app.utils.roles import role_required

router = APIRouter()


@router.get(
    "/jobs/available",
    response_model=List[JobRead],
    dependencies=[Depends(role_required("seeker"))],
)
async def get_available_jobs(
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]
    user = db.users.find_one({"_id": ObjectId(user_id)})

    if not user or "location" not in user:
        raise HTTPException(status_code=400, detail="User location not found")

    latitude = user["location"]["latitude"]
    longitude = user["location"]["longitude"]

    # Fetch jobs within a specified radius (e.g., 10km)
    nearby_jobs = db.jobs.find(
        {
            "location": {
                "$geoWithin": {
                    "$centerSphere": [
                        [longitude, latitude],
                        10
                        / 6378.1,  # Convert radius to radians (Earth's radius in km)
                    ]
                }
            }
        }
    )

    return [JobRead(id=str(job["_id"]), **job) for job in nearby_jobs]


@router.post(
    "/jobs/{job_id}/bid",
    dependencies=[Depends(role_required("seeker"))],
)
async def bid_on_job(
    job_id: str,
    bid: JobBid,
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]

    job = db.jobs.find_one({"_id": ObjectId(job_id)})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    db.jobs.update_one(
        {"_id": ObjectId(job_id)},
        {
            "$push": {
                "bids": {
                    "user_id": user_id,
                    "bid_amount": bid.bid_amount,
                }
            }
        },
    )

    return {"message": "Bid placed successfully"}


@router.post(
    "/jobs/{job_id}/accept",
    dependencies=[Depends(role_required("seeker"))],
)
async def accept_job(
    job_id: str, current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]

    job = db.jobs.find_one({"_id": ObjectId(job_id)})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job["accepted_by"]:
        raise HTTPException(status_code=400, detail="Job already accepted")

    db.jobs.update_one(
        {"_id": ObjectId(job_id)},
        {"$set": {"accepted_by": user_id, "status": "accepted"}},
    )

    return {"message": "Job accepted successfully"}
