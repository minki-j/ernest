from typing import Literal
from varname import nameof as n

from app.langchain.schema import Documents
from app.schemas.schemas import State
from app.langchain.nodes.llm.pick import random_one_on_one_match

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

    # TODO: change this to LLM call
    end_conversation = False

    if len(documents.review.messages) < 2:
        print("     : start")
        return "start_of_chat"
    elif end_conversation:
        print("     : end")
        return "end_of_chat"
    elif documents.review.vendor_id is None:
        return "ask_vendor_info"
    else:
        print("     : middle")
        return "middle_of_chat"


def is_tournament_complete(state: dict[str, Documents]):
    print("\n==>> is_tournament_complete")
    documents = state["documents"]

    if len(documents.state.tournament["players"]) == 1:
        print("     : Yes. Final option: ", documents.state.tournament["players"][0])
        return "__end__"
    else:
        print(f"     : No. {len(documents.state.tournament["players"])} players left")
        return n(random_one_on_one_match)
