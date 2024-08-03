"""
Module for city check schemas.

This module contains the request and response schemas for checking if a city is served.
"""

from pydantic import BaseModel


class CityCheckRequest(BaseModel):
    """
    Request schema for checking if a city is served.

    Attributes:
        city_id (str): The ID of the city to check.
    """

    city_id: str


class CityCheckResponse(BaseModel):
    """
    Response schema indicating if a city is served.

    Attributes:
        is_served (bool): A boolean indicating if the city is served.
    """

    is_served: bool
