import certifi
from pymongo import MongoClient

# Replace the following with your actual MongoDB connection string
MONGO_CONNECTION_STRING = (
    "mongodb+srv://workerllyapp:fGbE276ePop1iapV@backendking.y6lcith.mongodb.net/"
)

client = MongoClient(MONGO_CONNECTION_STRING, tlsCAFile=certifi.where())
db = client.workerlly  # Use the actual database name

db.users.create_index("mobile", unique=True)
db.categories.create_index("name", unique=True)
db.cities.create_index("name", unique=True)
