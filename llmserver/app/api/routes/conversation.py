from datetime import datetime
from bson.objectid import ObjectId

from fastapi import APIRouter, Form

from app.utils.twilio import send_sms
from app.utils.mongodb import fetch_documents, update_document, delete_document

from app.langchain.langgraph_main import langgraph_app
from app.schemas.schemas import Message
from app.langchain.common import Documents


router = APIRouter()


@router.get("/")
def root():
    return {"message": "Conversation API route working fine"}


@router.post("/chat")
def reply_to_message(
    user_id: str = Form(...),
    vendor_id: str = Form(...),
    review_id: str = Form(...),
    user_msg: str = Form(...),
    test: str = Form("false"),
    reset: str = Form("false"),
):
    test = test.lower() == "true"
    reset = reset.lower() == "true"

    if reset:
        delete_document(review_id)

    documents: Documents = fetch_documents(review_id, user_id, vendor_id)
    documents.update(
        Message(
            id=ObjectId(),
            role="user",
            content=user_msg,
            created_at=datetime.now().isoformat(),
            references=[],
        )
    )
    documents

    document = langgraph_app.invoke(document)

    was_update_successful = update_document(user_phone_number, document=document)

    if not was_update_successful:
        error_message = "Apologies for the inconvenience🙏🏻 We encountered an error while processing your message. Kindly try again later. If the issue persist, don't hesitate to reach out to us for assistance. Thank you for your understanding😊"
        send_sms(user_phone_number, error_message)
        return {"message": "updating MongoDB failed"}

    reply = document["ephemeral"]["reply_message"]
    if not test:
        send_sms(user_phone_number, reply)

    return {"message": reply}
