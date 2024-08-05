# app/api/v1/schemas/rate.py
from pydantic import BaseModel


class Rate(BaseModel):
    category_id: str
    city_id: str
    rate_per_hour: float
