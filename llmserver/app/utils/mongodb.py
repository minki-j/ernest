import os 
from datetime import datetime
from typing import List
from bson.objectid import ObjectId

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import ReturnDocument


from app.langchain.common import Documents

from app.schemas.schemas import Review, User, Vendor, State

uri = f"mongodb+srv://qmsoqm2:{os.environ["MONGO_DB_PASSWORD"]}@chathistory.tmp29wl.mongodb.net/?retryWrites=true&w=majority&appName=chatHistory"

def fetch_documents(review_id: str, user_id: str, vendor_id: str) -> Documents:
    client = MongoClient(uri, server_api=ServerApi('1'))

    db = client.get_database('ernest')
    
    user_collection = db.get_collection('user')
    user = user_collection.find_one_and_update(
            {"_id": user_id},
            {"$setOnInsert": vars(User())}, 
            upsert=True, 
            return_document=ReturnDocument.AFTER
        )
    if not user:
        raise ValueError(f"User with id {user_id} not found")
    
    vendor_collection: Vendor = db.get_collection('vendor')
    vendor = vendor_collection.find_one_and_update(
            {"_id": vendor_id},
            {"$setOnInsert": vars(Vendor())}, 
            upsert=True, 
            return_document=ReturnDocument.AFTER
        )
    if not vendor:
        raise ValueError(f"Vendor with id {vendor_id} not found")

    review_collection: Review = db.get_collection('review')
    review = review_collection.find_one_and_update(
        {"_id": review_id},
        {"$setOnInsert": vars(Review(user_id=user_id, vendor_id=vendor_id))},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    
    return Documents(
        review=Review(**review),
        user=User(**user),
        vendor=Vendor(**vendor),
        state=State(**review["state"])
    )

def update_document(review_id: str, user_id:str, vendor_id:str, document: dict) -> bool:
    client = MongoClient(uri, server_api=ServerApi('1'))

    db = client.get_database('ernest')

    user_collection= db.get_collection('user')
    result = user_collection.update_one({"_id": user_id}, {"$set": document["user"]})
    if not result:
        raise ValueError(f"User with id {user_id} update failed")
    
    vendor_collection= db.get_collection('vendor')
    result = vendor_collection.update_one({"_id": vendor_id}, {"$set": document["vendor"]})
    if not result:
        raise ValueError(f"Vendor with id {vendor_id} update failed")

    review_collection= db.get_collection('review')
    result = review_collection.update_one({"_id": review_id}, {"$set": document["review"]})
    if not result:
        raise ValueError(f"Review with id {review_id} update failed")

    return True

def delete_document(review_id: str) -> bool:
    client = MongoClient(uri, server_api=ServerApi('1'))

    db = client.get_database('ernest')
    review_collection= db.get_collection('review')
    review_collection.delete_one(
        {"_id": review_id}
    )

    return True
