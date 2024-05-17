import os 
from datetime import datetime
from typing import List
from bson.objectid import ObjectId

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import ReturnDocument

from app.utils.default_topics import DEFAULT_TOPICS

from app.langchain.common import Documents

from app.schemas.schemas import Review, User, Vendor

uri = f"mongodb+srv://qmsoqm2:{os.environ["MONGO_DB_PASSWORD"]}@chathistory.tmp29wl.mongodb.net/?retryWrites=true&w=majority&appName=chatHistory"

def fetch_documents(review_id: str, user_id: str, vendor_id: str) -> Documents:
    client = MongoClient(uri, server_api=ServerApi('1'))

    db = client.get_database('ernest')
    
    user_collection= db.get_collection('user')
    user = user_collection.find_one({"_id": user_id})
    if not user:
        raise ValueError(f"User with id {user_id} not found")
    
    vendor_collection= db.get_collection('vendor')
    vendor = vendor_collection.find_one({"_id": vendor_id})
    if not vendor:
        raise ValueError(f"Vendor with id {vendor_id} not found")

    review_collection= db.get_collection('review')
    review = review_collection.find_one_and_update(
        {"_id": review_id},
        {"$setOnInsert": Review(user_id=user_id, vendor_id=vendor_id)},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    
    return Documents(
        review=review,
        user=user,
        vendor=vendor,
        state=review["state"]
    )

def update_document(review_id: str, document: dict) -> bool:
    client = MongoClient(uri, server_api=ServerApi('1'))

    db = client.get_database('chat_history')
    history_collection= db.get_collection('history')
    history_collection.update_one(
        {"review_id": review_id}, 
        {'$set': document}
    )

    return True

def delete_document(review_id: str) -> bool:
    client = MongoClient(uri, server_api=ServerApi('1'))

    db = client.get_database('chat_history')
    history_collection= db.get_collection('history')
    history_collection.delete_one(
        {"review_id": review_id}
    )

    return True
