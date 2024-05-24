import os 
from datetime import datetime
from typing import List
from bson.objectid import ObjectId

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import ReturnDocument


from app.langchain.schema import Documents

from app.schemas.schemas import Review, User, Vendor, State, ParallelState

uri = f"mongodb+srv://qmsoqm2:{os.environ["MONGO_DB_PASSWORD"]}@chathistory.tmp29wl.mongodb.net/?retryWrites=true&w=majority&appName=chatHistory"

def fetch_document(review_id: str, user_id: str) -> Documents:
    client = MongoClient(uri, server_api=ServerApi('1'))

    db = client.get_database('ernest')
    
    user_collection = db.get_collection('user')
    user = user_collection.find_one_and_update(
            {"_id": user_id},
            {"$setOnInsert": User().to_dict()}, 
            upsert=True, 
            return_document=ReturnDocument.AFTER
        )
    if user is None:
        raise ValueError(f"User with id {user_id} not found")
    
    review_collection: Review = db.get_collection('review')
    review = review_collection.find_one_and_update(
        {"_id": review_id},
        {"$setOnInsert": Review(user_id=user_id).to_dict()},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    if review is None:
        raise ValueError(f"Review with id {review_id} not found")

    vendor_id = review.get("vendor_id", ObjectId())
    vendor_collection: Vendor = db.get_collection('vendor')
    vendor = vendor_collection.find_one_and_update(
            {"_id": vendor_id},
            {"$setOnInsert": Vendor().to_dict()}, 
            upsert=True, 
            return_document=ReturnDocument.AFTER
        )
    if vendor is None:
        raise ValueError(f"Vendor with id {vendor_id} not found")
    
    print(f"==>> fetch_document ran successfully")

    return Documents(
        review=Review(**review),
        user=User(**user),
        vendor=Vendor(**vendor),
        state=State(),
        parallel_state=ParallelState()
    )

def update_document(documents: Documents) -> bool:
    client = MongoClient(uri, server_api=ServerApi('1'))

    user_id = documents.user._id
    vendor_id = documents.vendor._id
    review_id = documents.review._id

    db = client.get_database('ernest')

    user_collection= db.get_collection('user')
    result = user_collection.update_one({"_id": user_id}, {"$set": documents.user.to_dict()})
    if not result:
        raise ValueError(f"User with id {user_id} update failed")
    
    vendor_collection= db.get_collection('vendor')
    result = vendor_collection.update_one({"_id": vendor_id}, {"$set": documents.vendor.to_dict()})
    if not result:
        raise ValueError(f"Vendor with id {vendor_id} update failed")

    review_collection= db.get_collection('review')
    result = review_collection.update_one({"_id": review_id}, {"$set": documents.review.to_dict()})
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

    print(f"==>> delete_document ran successfully")
    return True
