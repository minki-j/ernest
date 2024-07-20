from datetime import datetime
from bson.objectid import ObjectId

from fastapi import APIRouter, Form

from app.utils.mongodb import fetch_document, update_document, delete_document

from app.langchain.main_graph import langgraph_app
from app.schemas.schemas import Message, Role
from app.langchain.schema import Documents


router = APIRouter()


@router.get("/")
def root():
    return {"message": "/chat route working fine"}

@router.post("/add_ai_first_message")
def add_ai_first_message(
    user_email: str = Form(...),
    review_id: str = Form(...),
    message: str = Form(default=""),
):
    print("-->add_ai_first_message")
    documents: Documents = fetch_document(review_id, user_email)

    documents.add(
        Message(
            role=Role.AI,
            content=message,
        )
    )

    was_update_successful = update_document(documents)

    if not was_update_successful:
        return {"message": "updating MongoDB failed"}

    return {"message": "AI first message added"}


@router.post("/invoke")
def reply_to_message(
    user_email: str = Form(...),
    review_id: str = Form(...),
    user_msg: str = Form(default=""),
    test: str = Form(default="false"),
    reset: str = Form(default="false"),
):
    print("-->reply_to_message")
    test = test.lower() == "true"
    reset = reset.lower() == "true"

    if reset:
        delete_document(review_id)

    documents: Documents = fetch_document(review_id, user_email)

    if user_msg != "":
        documents.add(
            Message(
                role=Role.USER,
                content=user_msg,
            )
        )


    documents = langgraph_app.invoke(
        {"documents": documents},
        {"recursion_limit": 20},
    )["documents"]

    was_update_successful = update_document(documents)

    if not was_update_successful:
        return {"message": "updating MongoDB failed"}

    reply = (
        documents.state.reply_message
        if hasattr(documents.state, "reply_message")
        else "No reply provided"
    )
    ui_type = documents.state.ui_type if hasattr(documents.state, "ui_type") else "message"
    print(f"==>> ui_type: {ui_type}")

    return {"uiType": ui_type, "message": reply}
