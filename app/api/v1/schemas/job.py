from pydantic import BaseModel, Field
from typing import List, Optional

class JobCreate(BaseModel):
    title: str
    description: str
    category: str
    sub_category: str
    hourly_rate: float
    location: dict
    address: str
    start_date: str
    end_date: Optional[str]

class JobRead(BaseModel):
    id: str
    title: str
    description: str
    category: str
    sub_category: str
    hourly_rate: float
    location: dict
    address: str
    start_date: str
    end_date: Optional[str]
    created_by: str
    status: str
    accepted_by: Optional[str] = None
    bids: Optional[List[dict]] = Field(default_factory=list)

class JobBid(BaseModel):
    bid_amount: float
