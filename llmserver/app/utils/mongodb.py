import os 
from datetime import datetime
from typing import List
from bson.objectid import ObjectId

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import ReturnDocument

from app.utils.default_topics import DEFAULT_TOPICS

from app.langchain.states.document_state import DocumentState

uri = f"mongodb+srv://qmsoqm2:{os.environ["MONGO_DB_PASSWORD"]}@chathistory.tmp29wl.mongodb.net/?retryWrites=true&w=majority&appName=chatHistory"

def fetch_document(phone_number: str) -> DocumentState:
    client = MongoClient(uri, server_api=ServerApi('1'))

    try:
        db = client.get_database('chat_history')
        history_collection= db.get_collection('history')
        document = history_collection.find_one_and_update(
            {"phone_number": phone_number},
            {"$setOnInsert": {
                "phone_number": phone_number,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "user_info": {"age": "30"},
                "messages": [{'id': ObjectId(), 'role': 'ai', 'content': "Hey, how are you doing today", 'created_at': '2024-05-15T19:27:53.677708'}], 
                "topics": [*DEFAULT_TOPICS],
                "ephemeral": {
                    "current_topic_idx": 0,
                    "current_question_idx": 0,
                }
                }
            },
            upsert=True,
            return_document=ReturnDocument.AFTER
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

def delete_document(phone_number: str) -> bool:
    client = MongoClient(uri, server_api=ServerApi('1'))

    db = client.get_database('chat_history')
    history_collection= db.get_collection('history')
    history_collection.delete_one(
        {"phone_number": phone_number}
    )

    return True
