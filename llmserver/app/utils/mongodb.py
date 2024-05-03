import os 
from typing import List

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from bson.objectid import ObjectId

uri = f"mongodb+srv://qmsoqm2:{os.environ["MONGO_DB_PASSWORD"]}@chathistory.tmp29wl.mongodb.net/?retryWrites=true&w=majority&appName=chatHistory"


def fetch_chat_history(phone_number: str, n: int) -> List[str]:
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
    context = []

    user_info = ""
    for key, value in chat_history["user_info"].items():
        info = str(key) + ": " + str(value) + "\n"
        user_info += info
    context.append({"user_info": user_info})

    conversation = []
    if "messages" in chat_history:
        count = 0
        for msg in chat_history["messages"]:
            try:
                author_message_block = {
                    "role": msg["author"], 
                    "content": msg["message"]
                }
                conversation.append(author_message_block)
                count += 1
                if count == n:
                    break
            except:
                pass

    return context, conversation


def update_chat_history(phone_number: str, user_message: str, user_message_id: ObjectId, reply: str, reply_id: ObjectId, received_time: str, replied_time: str) -> bool:
    client = MongoClient(uri, server_api=ServerApi('1'))

    new_messages = [
        {
            "id": user_message_id,
            "author": "user",
            "message": user_message,
            "created_at": received_time,
        },
        {
            "id": reply_id,
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


def fetch_unasked_questions(phone_number: str) -> List[str]:
    client = MongoClient(uri, server_api=ServerApi('1'))

    try:
        db = client.get_database('chat_history')
        history_collection= db.get_collection('history')
        unasked_questions = history_collection.find(
            {"phone_number": phone_number}, 
            { 
                "questions": { 
                "$elemMatch": { "answer": ""}
                }
            },
            {
                "questions.question": 1,
                "_id": 0
            },
        )
        print(f"==>> unasked_questions type: {type(unasked_questions)}")
        print(f"==>> unasked_questions: {unasked_questions}")
    except Exception as e:
        print(e)
        return []
    
    return unasked_questions


def update_answer(phone_number: str, question: str, answer: str) -> bool:
    client = MongoClient(uri, server_api=ServerApi('1'))

    try:
        db = client.get_database('chat_history')
        history_collection= db.get_collection('history')
        history_collection.update_one(
            {"phone_number": phone_number, "questions.question": question},
            {"$set": {"questions.$.answer": answer}}
        )
    except Exception as e:
        print(e)
        return False

    return True

def get_relevant_question_from_message(phone_number: str,message: str) -> str:
    client = MongoClient(uri, server_api=ServerApi('1'))

    try:
        db = client.get_database('chat_history')
        history_collection = db.get_collection('history')

        messages = history_collection.find_one(
            {
                "phone_number": phone_number,
                'messages': { 
                    '$elemMatch': { 'message': message }
                }
            },
            {
                'messages.$': 1, # only return the matched element from the array.
                '_id': 0
            }
        )

        id_of_last_bot_message = messages["messages"][0]["id"]
        
        relevant_question = history_collection.find_one(
            {
                "phone_number": phone_number,
                'questions': { 
                    '$elemMatch': { 'reference_message_ids': id_of_last_bot_message }
                }
            },
            {
                'questions.$': 1, # only return the matched element from the array.
                '_id': 0
            }
        )
        
    except Exception as e:
        print(e)
        return None

    return relevant_question["questions"][0] if relevant_question else None


def update_question_answer(phone_number: str, ref_message_ids: List[ObjectId], answer: str, enoughness_score: int) -> bool:
    client = MongoClient(uri, server_api=ServerApi('1'))

    try:
        db = client.get_database('chat_history')
        history_collection= db.get_collection('history')
        history_collection.update_one(
            {"phone_number": phone_number},
            {
                "$push": {"reference_message_ids": ref_message_ids},
                "$set": {"answer": answer},
                "$set": {"enoughness_score": enoughness_score}
            }
        )
    except Exception as e:
        print(e)
        return False

    return True
