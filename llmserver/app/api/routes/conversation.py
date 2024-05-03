from fastapi import APIRouter, Form, Response
from pydantic import BaseModel
from datetime import datetime

import dspy
from app.dspy.modules.chatbot import Chatbot
from app.dspy.modules.intent_classifier import IntentClassifierModule


from app.utils.twilio import send_sms

from app.utils.mongodb import (
    fetch_chat_history,
    update_chat_history,
    update_question_answer,
)


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
    received_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    user_message = Body
    user_phone_number = From

    context, conversation = fetch_chat_history(
        phone_number=user_phone_number,
        n=4,
    )

    conversation.append({"role": "user", "content": user_message})

    if model == "llama3_8b":
        if vllm:
            chatbot = Chatbot(lm_name="llama3_8b_on_vllm")
        else:
            chatbot = Chatbot(lm_name="llama3_8b")
    else:
        chatbot = Chatbot(lm_name="gpt-3.5-turbo")

    pred = chatbot.forward(user_phone_number, context, conversation)

    # send_sms(pred.reply, user_phone_number)

    replied_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # update_chat_history(
    #     user_phone_number,
    #     user_message=user_message,
    #     user_message_id=pred.user_message_id,
    #     reply=pred.reply,
    #     reply_id=pred.reply_id,
    #     received_time=received_time,
    #     replied_time=replied_time,
    # )

    update_question_answer(
        user_phone_number,
        ref_message_ids=[
            pred.user_message_id,
        ],
        answer=pred.updated_answer,
        enoughness_score=pred.enoughness_score,
    )

    print("---------lm.inspect_history-----------")
    print(dspy.settings.lm.inspect_history(n=1))
    print("LLM: ", dspy.settings.lm)
    print("---------lm.inspect_history-----------")

    return {"message": pred.reply}
