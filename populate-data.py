import certifi
from pymongo import MongoClient

MONGO_CONNECTION_STRING = (
    "mongodb+srv://workerllyapp:fGbE276ePop1iapV@backendking.y6lcith.mongodb.net/"
)

client = MongoClient(MONGO_CONNECTION_STRING, tlsCAFile=certifi.where())
db = client.workerlly  # Use the actual database name

# Sample data for categories
categories = [
    {
        "name": "Electrical",
        "sub_categories": [
            {"id": "1", "name": "Wiring"},
            {"id": "2", "name": "Lighting"},
            {"id": "3", "name": "Appliance Repair"},
        ],
    },
    {
        "name": "Plumbing",
        "sub_categories": [
            {"id": "4", "name": "Leak Repair"},
            {"id": "5", "name": "Pipe Installation"},
            {"id": "6", "name": "Drain Cleaning"},
        ],
    },
    {
        "name": "Home Cleaning",
        "sub_categories": [
            {"id": "7", "name": "General Cleaning"},
            {"id": "8", "name": "Deep Cleaning"},
            {"id": "9", "name": "Carpet Cleaning"},
        ],
    },
]

# Sample data for cities
cities = [
    {"name": "Panchkula"},
    {"name": "Delhi"},
    {"name": "Mumbai"},
    {"name": "Bangalore"},
]

# Insert data into categories and cities collections
db.categories.insert_many(categories)
db.cities.insert_many(cities)
