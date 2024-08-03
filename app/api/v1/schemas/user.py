from typing import Optional, List

from bson import ObjectId
from pydantic import BaseModel


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class UserSchema(BaseModel):
    mobile: str
    roles: List[str]


class UserRead(BaseModel):
    id: str
    mobile: str
    roles: List[str]
    name: Optional[str] = None
    city: Optional[str] = None
    skills: Optional[List[str]] = []
    experience: Optional[int] = 0
    rating: Optional[float] = 0.0


class ProfileComplete(BaseModel):
    name: str
    category: str
    sub_category: List[str]
    city: str
    experience: Optional[int]
