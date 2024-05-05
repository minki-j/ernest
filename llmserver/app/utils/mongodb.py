import os 
from datetime import datetime
from typing import List

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from bson.objectid import ObjectId

import dspy
from app.dspy.signatures.signatures import PurePrompt
from app.dspy.utils.initialize_DSPy import initialize_DSPy

uri = f"mongodb+srv://qmsoqm2:{os.environ["MONGO_DB_PASSWORD"]}@chathistory.tmp29wl.mongodb.net/?retryWrites=true&w=majority&appName=chatHistory"

def fetch_document(phone_number: str) -> dict:
    client = MongoClient(uri, server_api=ServerApi('1'))

    try:
        db = client.get_database('chat_history')
        history_collection= db.get_collection('history')
        document = history_collection.find_one(
            {
                "phone_number": phone_number,
            },
            {
                '_id': 0
            }
        )
    except Exception as e:
        print(e)
        return None

    return document

def update_document(phone_number: str, document: dict) -> bool:
    client = MongoClient(uri, server_api=ServerApi('1'))

    db = client.get_database('chat_history')
    history_collection= db.get_collection('history')
    history_collection.update_one(
        {"phone_number": phone_number}, 
        {'$set': document}
    )

    return True
