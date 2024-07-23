from typing import Literal
from varname import nameof as n

from app.langchain.schema import Documents
from app.schemas.schemas import Role
from app.langchain.nodes.llm.pick import random_one_on_one_match

from langchain_core.prompts import PromptTemplate
from app.langchain.common import chat_model

from langchain_core.pydantic_v1 import BaseModel, Field


def what_stage_of_chat(state: dict[str, Documents]):
    print("\n==>> what_stage_of_chat")
    documents = state["documents"]

    # TODO: change this to LLM call
    end_conversation = False if len(documents.review.messages) < 20 else True

    if len(documents.review.messages) <= 1 or not documents.vendor.name:
        print("     : start")
        return "start_of_chat"
    elif end_conversation:
        print("     : end")
        return "end_of_chat"
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
