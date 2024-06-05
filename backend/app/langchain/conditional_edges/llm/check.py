from varname import nameof as n
from typing import Literal
from enum import Enum

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from app.langchain.schema import Documents
from app.schemas.schemas import State
from app.langchain.utils.converters import messages_to_string

from app.langchain.nodes.llm.generate import generate_reply
from app.langchain.nodes.llm.criticize import reflection
from app.langchain.subgraphs.middle_of_chat.gather_context.graph import gather_context
from app.langchain.subgraphs.middle_of_chat.extract.graph import extract

from app.langchain.conditional_edges.non_llm.simple_check import what_stage_of_chat
from app.langchain.nodes.non_llm.predefined_reply import reply_for_incomplete_msg

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

message: "I am going to the"
judgement: True

message: "I am going to the store."
judgement: False

message: "hi"
judgement: False

message: "hi, how are you?"
judgement: False

message: "I was at the store wit"
judgement: True

message: "Yes I did. I showed a picture of hair style that I wanted. But the hairstylist glanced it and kind of ignored me."
judgement: False


Now it's your turn
message: {message}

"""
    )

    chain = prompt | chat_model_openai_4o.with_structured_output(
        IsMSGCutOff
    ).with_config(configurable={"llm_temperature": 0})

    is_msg_complete = chain.invoke(
        {
            "message": messages_to_string(documents.review.messages[-1:])
        }
    )
    print("     judgement:", is_msg_complete.judgement)

    if is_msg_complete.judgement:
        return n(reply_for_incomplete_msg)
    else:
        return n(extract)
