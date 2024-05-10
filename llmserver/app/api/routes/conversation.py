from fastapi import APIRouter, Form, Response
from pydantic import BaseModel
from datetime import datetime
from bson.objectid import ObjectId

import dspy
from app.dspy.modules.chatbot import Chatbot
from app.dspy.modules.intent_classifier import IntentClassifierModule

from pprint import pprint

from app.utils.twilio import send_sms

from app.utils.mongodb import fetch_document, update_document

from app.langchain.reply_chat import langgraph_app

class QuestionRequest(BaseModel):
    message: str


router = APIRouter()


@router.get("/")
def root():
    return {"message": "Conversation API route working fine"}


@router.post("/chat")
def reply_to_message(
    From: str = Form(...),
    Body: str = Form(...),
    model: str = "gpt-3.5-turbo",
    vllm: bool = True,
):
    user_message = Body
    user_phone_number = From

    document = fetch_document(user_phone_number)
    document.setdefault("messages", []).append(
        {
            "id": ObjectId(),
            "role": "user",
            "content": user_message,
            "created_at": datetime.now().isoformat(),
        }
    )
    document["ephemeral"] = {
        "enoughness_threshold": 0.8,
    }
    # document type = langgraph.graph.state.compiledStateGraph
    document = langgraph_app.invoke(document)
    print(f"==>> document keys: {document.keys()}")
    print(f"==>> message: {document["ephemeral"]["message"]}")

    reply = document["ephemeral"]["message"]

    # drop the ephemeral key
    document["ephemeral"] = {}

    # send_sms(user_phone_number, reply)

    was_successful = update_document(user_phone_number, document=document)

    if not was_successful:
        return {"message": "ERROR: Could not update the backend."}

    return {"message": reply}
