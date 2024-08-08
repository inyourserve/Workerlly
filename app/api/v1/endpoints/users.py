import secrets
from datetime import datetime, timedelta
from typing import List
import jwt
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
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


class AuthRequest(BaseModel):
    mobile: str
    otp: str
    roles: List[str]


@router.post("/users/register")
def register_user(user: UserSchema):
    print(f"Registering user with mobile: {user.mobile} and roles: {user.roles}")
    if not send_otp(user.mobile):
        raise HTTPException(status_code=500, detail="Failed to send OTP")
    return {"message": "OTP sent to mobile"}


@router.post("/users/auth")
def authenticate_user(auth_request: AuthRequest):
    mobile = auth_request.mobile
    otp = auth_request.otp
    roles = auth_request.roles

    print(f"Authenticating user with mobile: {mobile} and roles: {roles}")
    if not verify_otp(mobile, otp):
        raise HTTPException(status_code=400, detail="Invalid OTP")

    existing_user = db.users.find_one({"mobile": mobile})
    if not existing_user:
        print("User does not exist, creating a new one.")
        result = db.users.insert_one(
            {"mobile": mobile, "roles": list(set(roles)), "status": False}
        )
        user_id = result.inserted_id  # Get the MongoDB ObjectId
    else:
        user_id = existing_user["_id"]
        existing_roles = set(existing_user.get("roles", []))
        new_roles = set(roles)
        updated_roles = list(
            existing_roles.union(new_roles)
        )  # Merge and remove duplicates
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
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/me1")
def get_current_user(
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]
    # Convert user_id from string to ObjectId

    # Convert user_id from string to ObjectId
    object_id = ObjectId(user_id)

    # Fetch user details from the database using the ObjectId
    user_details = db.users.find_one({"_id": object_id})
    if not user_details:
        raise HTTPException(status_code=404, detail="User not found")

    # Convert ObjectId fields to string for JSON serialization
    user_details["_id"] = str(user_details["_id"])
    if "city_id" in user_details:
        user_details["city_id"] = str(user_details["city_id"])
    if "category_id" in user_details:
        user_details["category_id"] = str(user_details["category_id"])
    if "sub_category_id" in user_details:
        user_details["sub_category_id"] = [
            str(sub_id) for sub_id in user_details["sub_category_id"]
        ]

    return user_details


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
        status=user_details.get(
            "status", False
        ),  # Ensure status has a default value of False
        name=user_details.get("name"),
        city=user_details.get("city"),
        skills=user_details.get("skills", []),
        experience=user_details.get("experience", 0),
        rating=user_details.get("rating", 0.0),
    )
