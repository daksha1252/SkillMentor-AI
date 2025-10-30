import os
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI")  # Set in environment variables
client = MongoClient(MONGO_URI)
db = client['skillmentor']  # Database
users_col = db['users']     # Collection

def get_user_data(user_id):
    return users_col.find_one({"user_id": user_id})

def save_user_data(user_id, email, resume_text, interests, career_goal, analysis_result):
    users_col.update_one(
        {"user_id": user_id},
        {"$set": {
            "email": email,
            "resume_text": resume_text,
            "interests": interests,
            "career_goal": career_goal,
            "analysis_result": analysis_result
        }},
        upsert=True
    )
