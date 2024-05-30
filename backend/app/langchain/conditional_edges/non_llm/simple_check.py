from typing import Literal

from app.langchain.schema import Documents
from app.schemas.schemas import State

def is_user_name(state: dict[str, Documents]):
    print("\n==>> is_user_name")
    documents = state["documents"]

    if documents.user.name is None:
        return "ask_name"
    else:
        return "greeting"


def what_stage_of_chat(state: dict[str, Documents]):
    print("\n==>> is_start_of_chat")
    documents = state["documents"]
    print("    messages", documents.review.messages)

    # TODO: change this to LLM call
    end_conversation = False

    if len(documents.review.messages) < 2:
        print("     : start")
        return "start_of_chat"
    elif end_conversation:
        print("     : end")
        return "end_of_chat"
    else:
        print("     : middle")
        return "middle_of_chat"

