from fastapi import APIRouter, Form, Response
from pydantic import BaseModel
from datetime import datetime

import dspy
from app.dspy.modules.chatbot import Chatbot
from app.dspy.modules.intent_classifier import IntentClassifierModule

from pprint import pprint

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
    user_message = Body
    user_phone_number = From
    enoughness_threshold = 0.5

    # update the answer based on the user's last message
    result= update_question_answer(
            user_phone_number=user_phone_number,
            user_message=user_message,
            n=4,
            enoughness_threshold=enoughness_threshold,
        )
    print("updated answer: ", result["updated_answer"])

    # !! TODO: relevant question can be more than one. Need a better way to detect and handle it. In the meantime, I'll just assume that the user replied to the lastest question.
    chat_data = {
        "relevant_question": result["relevant_question"],
        "updated_answer": result["updated_answer"],
        "ref_message_ids": result["ref_message_ids"],
        "unasked_questions": result["unasked_questions"],
        "messages": result["document"]["messages"],
        "context": result["document"]["user_info"],
        "enoughness_threshold": enoughness_threshold,
    }

    if model == "llama3_8b":
        if vllm:
            chatbot = Chatbot(lm_name="llama3_8b_on_vllm")
        else:
            chatbot = Chatbot(lm_name="llama3_8b")
    elif model == "claude-3-haiku-20240307":
        chatbot = Chatbot(lm_name="claude-3-haiku-20240307")
    else:
        chatbot = Chatbot(lm_name="gpt-3.5-turbo")

    pred = chatbot.forward(chat_data)

    # send_sms(pred.reply, user_phone_number)

    was_successful = update_chat_history(
        user_phone_number,
        chat_data=chat_data,
        reply=pred.reply,
        next_question=pred.next_question,
    )

    if not was_successful:
        # TODO: delete updated answer from the database
        return {"message": "ERROR: Could not update chat history."}

    return {"message": pred.reply if pred else "ERROR: pred is None"}
