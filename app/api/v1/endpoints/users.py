import secrets
from datetime import datetime, timedelta
from typing import List

import jwt
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import APIKeyHeader

from app.api.v1.schemas.user import UserSchema, UserRead
from app.db.models.database import db
from app.utils.msg91 import send_otp, verify_otp

router = APIRouter()

# APIKeyHeader is a class that provides an authentication mechanism
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)
# Secret key and algorithm for JWT token generation
SECRET_KEY = secrets.token_hex(32)  # Generates a 64-character hexadecimal string
ALGORITHM = "HS256"


# Function to create an access token using JWT
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=600)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/users/register")
def register_user(user: UserSchema):
    print(f"Registering user with mobile: {user.mobile} and roles: {user.roles}")
    if not send_otp(user.mobile):
        raise HTTPException(status_code=500, detail="Failed to send OTP")
    return {"message": "OTP sent to mobile"}


@router.post("/users/auth")
def authenticate_user(mobile: str, otp: str, roles: List[str]):
    print(f"Authenticating user with mobile: {mobile} and roles: {roles}")
    if not verify_otp(mobile, otp):
        raise HTTPException(status_code=400, detail="Invalid OTP")

    existing_user = db.users.find_one({"mobile": mobile})
    if not existing_user:
        print("User does not exist, creating a new one.")
        result = db.users.insert_one({"mobile": mobile, "roles": roles})
        user_id = result.inserted_id  # Get the MongoDB ObjectId
    else:
        user_id = existing_user["_id"]
        existing_roles = existing_user.get("roles", [])
        updated_roles = list(set(existing_roles + roles))  # Merge and remove duplicates
        db.users.update_one({"_id": user_id}, {"$set": {"roles": updated_roles}})
        roles = updated_roles
        print(f"Updated roles for user: {updated_roles}")

    # Generate a JWT token for the user with user_id and roles
    token = create_access_token(
        data={
            "user_id": str(user_id),
            "mobile": mobile,
            "roles": roles,
        }
    )

    return {"access_token": token, "token_type": "bearer"}


def get_current_user(api_key: str = Depends(api_key_header)):
    if not api_key:
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = api_key.split(" ")[1] if api_key.startswith("Bearer ") else api_key
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        mobile: str = payload.get("mobile")
        user_id: str = payload.get("user_id")
        roles: List[str] = payload.get("roles", [])
        if mobile is None or not roles:
            raise HTTPException(status_code=400, detail="Invalid token")
        return {"user_id": user_id, "mobile": mobile, "roles": roles}
    except jwt.JWTError:
        raise HTTPException(status_code=400, detail="Invalid token")


@router.get("/me", response_model=UserRead)
def get_current_user_endpoint(
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]
    # Convert user_id from string to ObjectId
    object_id = ObjectId(user_id)

    # Fetch user details from the database using the ObjectId
    user_details = db.users.find_one({"_id": object_id})
    if not user_details:
        raise HTTPException(status_code=404, detail="User not found")

    # Optionally, return any specific user details
    return UserRead(
        id=str(user_details["_id"]),
        mobile=user_details["mobile"],
        roles=user_details["roles"],
        name=user_details.get("name"),
        city=user_details.get("city"),
        skills=user_details.get("skills", []),
        experience=user_details.get("experience", 0),
        rating=user_details.get("rating", 0.0),
    )
