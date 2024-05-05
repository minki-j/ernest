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
    document["messages"].append(
        {
            "id": ObjectId(),
            "role": "user",
            "content": user_message,
            "created_at": datetime.now().isoformat(),
        }
    )

    if model == "llama3_8b":
        if vllm:
            chatbot = Chatbot(lm_name="llama3_8b_on_vllm")
        else:
            chatbot = Chatbot(lm_name="llama3_8b")
    elif model == "claude-3-haiku-20240307":
        chatbot = Chatbot(lm_name="claude-3-haiku-20240307")
    else:
        chatbot = Chatbot(lm_name="gpt-3.5-turbo")

    pred = chatbot.forward(document)

    reply = pred.reply
    new_document = pred.new_document

    send_sms(user_phone_number, reply)

    was_successful = update_document(user_phone_number, document=new_document)

    if not was_successful:
        return {"message": "ERROR: Could not update the backend."}

    return {"message": reply}
