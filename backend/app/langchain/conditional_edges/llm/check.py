from varname import nameof as n
from typing import Literal
from enum import Enum

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from app.langchain.schema import Documents
from app.schemas.schemas import Role
from app.langchain.utils.converters import messages_to_string

from app.langchain.nodes.llm.generate import generate_reply
from app.langchain.nodes.llm.criticize import reflection
from app.langchain.subgraphs.middle_of_chat.gather_context.graph import gather_context
from app.langchain.subgraphs.middle_of_chat.extract.graph import extract

from app.langchain.conditional_edges.non_llm.simple_check import what_stage_of_chat
from app.langchain.nodes.non_llm.predefined_reply import reply_for_incomplete_msg
from app.langchain.nodes.non_llm.predefined_reply import ask_user_name
from app.langchain.nodes.non_llm.predefined_reply import ask_vendor_info
from app.langchain.nodes.non_llm.predefined_reply import introduction

from app.langchain.common import llm, chat_model, output_parser, chat_model_openai_4o

from langchain_core.pydantic_v1 import BaseModel, Field


class IsMSGCutOff(BaseModel):
    """Check if the message is cut off or not."""

    judgement: bool = Field(description="True if the message is cut off, False otherwise.")


def is_msg_cut_off(state: dict[str, Documents]):
    print("\n==>> is_msg_cut_off")
    documents = state["documents"]

    prompt = PromptTemplate.from_template(
        """
Check if the message is cut off in the middle of a sentence. If the message completed with a full sentence, then it's not cut off. Otherwise, it's cut off.

Examples:

message: I am going to the store.
is_cut_off: False

message: hi
is_cut_off: False

message: hi, how are you?
is_cut_off: False

message: I just had a hair cut and don't like it
is_cut_off: False

message: Yes I did. I showed a picture of hair style that I wanted. But the hairstylist glanced it and kind of ignored me.
is_cut_off: False

message: I was at the store wit
is_cut_off: True

message: I just finished my first intership day and so disappointed...
is_cut_off: False


Now it's your turn
message: {message}

"""
    )

    chain = prompt | chat_model_openai_4o.with_config(
        configurable={"llm_temperature": 0.1}
    ).with_structured_output(IsMSGCutOff)

    user_message = documents.review.messages[-1].content
    # add . if not present at the end of the string to make the test more robust
    if user_message[-1] != ".":
        user_message += "."

    is_msg_complete = chain.invoke({"message": user_message})
    print("     judgement:", is_msg_complete.judgement)

    if is_msg_complete.judgement:
        return n(reply_for_incomplete_msg)
    else:
        return n(extract)


class ExtractedName(BaseModel):
    name: str = Field(description="The extracted name of the user")

def check_necessary_inquiries(state: dict[str, Documents]):
    print("\n==>> check_necessary_inquiries")
    documents = state["documents"]

    is_named_extacted = documents.user.name
    print(f"==>> is_named_extacted: {is_named_extacted}")
    is_vendor_extracted = documents.vendor.name if hasattr(documents, 'vendor') else None
    print(f"==>> is_vendor_extracted: {is_vendor_extracted}")

    if not is_named_extacted:
        return n(ask_user_name)
    elif not is_vendor_extracted:
        return n(ask_vendor_info)
    else:
        return n(introduction)
