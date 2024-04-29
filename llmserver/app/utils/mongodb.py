import os 
from typing import List

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from bson.objectid import ObjectId


def fetch_chat_history(phone_number: str, n: int) -> List[str]:
    uri = f"mongodb+srv://qmsoqm2:{os.environ["MONGO_DB_PASSWORD"]}@chathistory.tmp29wl.mongodb.net/?retryWrites=true&w=majority&appName=chatHistory"
    client = MongoClient(uri, server_api=ServerApi('1'))

    try:
        db = client.get_database('chat_history')
        history_collection= db.get_collection('history')
        chat_history = list(history_collection.find({"phone_number": phone_number}))[0]
    except Exception as e:
        chat_history = None
        print(e)

    if chat_history is None:
            return {"message": "No chat history found"}

    user_info = ""
    for key, value in chat_history["user_info"].items():
        info = str(key) + ": " + str(value) + "\n"
        user_info += info

    previous_messages = ""
    if "messages" in chat_history:
        count = 0
        for msg in chat_history["messages"]:
            try:
                author_message_block = msg["author"] + ": " + msg["message"] + "\n"
                previous_messages += author_message_block
                count += 1
                if count == n:
                    break
            except:
                pass
    else:
        previous_messages = "No previous messages provided."

    return user_info, previous_messages


def update_chat_history(phone_number: str, user_message: str, reply: str, received_time: str, replied_time: str) -> bool:
    uri = f"mongodb+srv://qmsoqm2:{os.environ["MONGO_DB_PASSWORD"]}@chathistory.tmp29wl.mongodb.net/?retryWrites=true&w=majority&appName=chatHistory"
    client = MongoClient(uri, server_api=ServerApi('1'))

    new_messages = [
        {
            "author": "user",
            "message": user_message,
            "created_at": received_time,
        },
        {
            "author": "bot",
            "message": reply,
            "created_at": replied_time,
        },
    ]

    try:
        db = client.get_database('chat_history')
        history_collection= db.get_collection('history')
        history_collection.update_one({"phone_number": phone_number}, {'$push': {'messages': {'$each': new_messages}}})
    except Exception as e:
        print(e)
        return False

    return True
