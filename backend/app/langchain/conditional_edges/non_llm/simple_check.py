from typing import Literal
from varname import nameof as n

from app.langchain.schema import Documents
from app.schemas.schemas import State
from app.langchain.nodes.llm.pick import random_one_on_one_match

from langchain_core.prompts import PromptTemplate
from app.langchain.common import chat_model

from langchain_core.pydantic_v1 import BaseModel, Field

class ExtractedName(BaseModel):
    name: str = Field(description="The extracted name of the user")

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
    print("messages:", documents.review.messages)
    last_AI_message = documents.review.messages[-2].content
    last_user_message = documents.review.messages[-1].content

    # TODO: change this to LLM call
    end_conversation = False

    is_reply_for_start_of_chat = (last_AI_message == "Hi I'm Ernest! What's your name?")

    if is_reply_for_start_of_chat:
        prompt = PromptTemplate.from_template(
            """
            Extract the user's name from the following message:
            {message}
            Only return the name, nothing else.
            """
        )
        chain = prompt | chat_model.with_structured_output(ExtractedName)
        user_name = chain.invoke({"message":last_user_message}).name
        print("update username with ", user_name)
        documents.user.name = user_name

    asked_vendor_info = (last_AI_message == "Before begin the interview, could you let me know which company or tool you are going to talk about?")

    if len(documents.review.messages) <= 1:
        print("     : start")
        return "start_of_chat"
    elif end_conversation:
        print("     : end")
        return "end_of_chat"
    elif not (documents.review.vendor_id or asked_vendor_info):
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
