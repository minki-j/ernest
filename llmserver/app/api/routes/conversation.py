from fastapi import APIRouter, Form, Response
from pydantic import BaseModel
from datetime import datetime


from app.dspy.modules.chatbot import Chatbot

from app.utils.twilio import send_sms

from app.utils.mongodb import fetch_chat_history, update_chat_history


class QuestionRequest(BaseModel):
    message: str


router = APIRouter()


@router.get("/")
def root():
    return {"message": "Conversation API route working fine"}


@router.post("/chat")
def reply_to_message(From: str = Form(...), Body: str = Form(...)):
    received_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_message = Body
    user_phone_number = From

    user_info, previous_messages = fetch_chat_history(phone_number=user_phone_number)

    chatbot = Chatbot(lm_name="llama3_8b_on_vllm")
    pred = chatbot.forward(user_info, previous_messages, user_message)

    send_sms(pred.reply, user_phone_number)

    replied_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    update_chat_history(
        user_phone_number,
        user_message=user_message,
        reply=pred.reply,
        received_time=received_time,
        replied_time=replied_time,
    )

    return {"message": pred.reply}
