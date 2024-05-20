from datetime import datetime
from bson.objectid import ObjectId

from fastapi import APIRouter, Form

from app.utils.mongodb import fetch_document, update_document, delete_document

from app.langchain.main_graph import langgraph_app
from app.schemas.schemas import Message, Role
from app.langchain.common import Documents


router = APIRouter()


@router.get("/")
def root():
    return {"message": "/conversation/ route working fine"}


@router.post("/chat")
def reply_to_message(
    user_id: str = Form(...),
    review_id: str = Form(...),
    user_msg: str = Form(default=""),
    test: str = Form(default="false"),
    reset: str = Form(default="false"),
):
    test = test.lower() == "true"
    reset = reset.lower() == "true"

    if reset:
        delete_document(review_id)

    documents: Documents = fetch_document(review_id, user_id)

    if user_msg != "":
        documents.add(
            Message(
                role=Role.USER,
                content=user_msg,
            )
        )

    # TODO: not working with Document class as a state type
    # print(langgraph_app.get_graph().draw_ascii())
    
    documents = langgraph_app.invoke({"documents": documents})["documents"]

    was_update_successful = update_document(documents)

    if not was_update_successful:
        return {"message": "updating MongoDB failed"}

    reply = documents.state.reply_message

    return {"message": reply}
