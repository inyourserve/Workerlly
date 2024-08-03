import certifi
from pymongo import MongoClient

MONGO_CONNECTION_STRING = (
    "mongodb+srv://workerllyapp:fGbE276ePop1iapV@backendking.y6lcith.mongodb.net/"
)
client = MongoClient(MONGO_CONNECTION_STRING, tlsCAFile=certifi.where())
db = client.workerlly  # Use the actual database name

# Sample data for rates
rates = [
    {
        "city": "Panchkula",
        "category": "Electrical",
        "rate_per_hour": 200,
    },
    {"city": "Delhi", "category": "Plumbing", "rate_per_hour": 250},
    {
        "city": "Mumbai",
        "category": "Home Cleaning",
        "rate_per_hour": 150,
    },
    {
        "city": "Bangalore",
        "category": "Electrical",
        "rate_per_hour": 220,
    },
]

# Insert data into rates collection
db.rates.insert_many(rates)
