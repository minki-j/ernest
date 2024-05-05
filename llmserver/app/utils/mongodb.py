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


def update_chat_history(phone_number: str, chat_data: dict, reply: str, next_question: str) -> bool:
    print("chat_data: ", chat_data)
    client = MongoClient(uri, server_api=ServerApi('1'))

    user_message = chat_data["messages"][-1]
    bot_message = {"id": ObjectId(), "role": "bot", "content": reply, "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    new_messages = [user_message, bot_message]

    relevant_question = chat_data.get("relevant_question", None)

    db = client.get_database('chat_history')
    history_collection= db.get_collection('history')
    history_collection.update_one(
        {"phone_number": phone_number}, 
        {'$push': {'messages': {'$each': new_messages}}}
    )
    if relevant_question or next_question:
        print("append ref message ids: ", chat_data["ref_message_ids"])
        history_collection.update_one(
            {"phone_number": phone_number,
                "questions.question": relevant_question["question"]},
            {"$set": {"questions.$.answer": chat_data["updated_answer"], "questions.$.enough": 1.0},
                "$push": {"questions.$.reference_message_ids": chat_data["ref_message_ids"]}}
        )


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


def update_question_answer(user_phone_number: str, user_message: str, n: int, enoughness_threshold: float) -> bool:
    '''Based on the user's new message, update the answer of the relevant question. And return the whole context and conversation along with the updated question object.'''
    client = MongoClient(uri, server_api=ServerApi('1'))
    try:
        db = client.get_database('chat_history')
        history_collection= db.get_collection('history')
        # first find the relevant question by looking up the latest bot's message
        document = history_collection.find_one(
            {
                "phone_number": user_phone_number,
            },
            {
                '_id': 0
            }
        )
    except Exception as e:
        print(e)
        return False
    
    id_of_last_bot_message = None
    revered_messages = document["messages"].reverse()
    if revered_messages:
        for msg in revered_messages:
            if msg["role"] == "bot":
                id_of_last_bot_message = msg["id"]
                break
    
    message_id = ObjectId()
    document["messages"].append({"id": message_id, "role": "user", "content": user_message, "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

    relevant_question = None
    ref_message_ids = None
    for question in document["questions"]:
        if id_of_last_bot_message in question["reference_message_ids"]:
            relevant_question = question
            ref_message_ids = question["reference_message_ids"]
            question["reference_message_ids"].append(message_id)
            break


    unasked_questions = [question for question in document["questions"] if question["enough"] < enoughness_threshold]

    if not relevant_question:
        print("No relevant question found")
        updated_answer = None
    else:
        updated_answer = update_answer(relevant_question, user_message)
        for question in document["questions"]:
            if question["question"] == relevant_question["question"]:
                question["answer"] = updated_answer
                break

    return {
        "relevant_question": relevant_question,
        "updated_answer": updated_answer,
        "ref_message_ids": ref_message_ids,
        "unasked_questions": unasked_questions,
        "document": document,
    }

def update_answer(relevant_question, user_message):
    question_content = relevant_question["question"]
    original_answer = relevant_question.get("answer", "")

    prompt = f'''
Update the answer of the following question based on the user's last message:\n
---\n
Example\n
\n
Question: how was the assignments of the course?\n
Previous Answer: It was too much for me. 
User's Last Message: I mean, there were 3 assignment in total every week and it took 3 hours to complete. I think it was too much for me. Also, the deadline was too short. And some of the assignments were too messy and not clearly explained.\n
Output: The workload was overwhelming with three assignments each week, each requiring three hours to complete and with tight deadlines. Moreover, some of the assignments were disorganized and lacked clear instructions.\n
---\n
Question: {question_content}\n
Previous Answer: {original_answer or "not answered yet"}\n
User's Last Message: {user_message}\n
'''

    initialize_DSPy(lm_name="gpt-3.5-turbo")
    pure_prompt = dspy.Predict(PurePrompt)
    updated_answer = pure_prompt(prompt=prompt).output
    print("updated_answer: ", updated_answer)

    print("---------lm.inspect_history-----------")
    print(dspy.settings.lm.inspect_history(n=1))
    print("LLM: ", dspy.settings.lm)
    print("---------lm.inspect_history-----------")

    return updated_answer
