from pydantic import BaseModel

class CityCheckRequest(BaseModel):
    city_id: str

class CityCheckResponse(BaseModel):
    is_served: bool