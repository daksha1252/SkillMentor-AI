from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)  # 5s timeout
try:
    print(client.list_database_names())
    print("Connection successful!")
except Exception as e:
    print("Connection failed:", e)
