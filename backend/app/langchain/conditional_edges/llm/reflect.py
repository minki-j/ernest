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

class IsPickedMissingDetailAppropriate(BaseModel):
    """Check if the picked missing detail is appropriate."""

    judgement: bool = Field(description="True if the picked missing detail is appropriate, False otherwise.")

def reflect_picked_missing_detail(state: dict[str, Documents]):
    print("\n==>> reflect_pick_missing_detail")
    documents = state["documents"]

    prompt = PromptTemplate.from_template(
        """
You are a journalist at a famous magazine with 40+ years of experience. Your main area of topic is about how customers experienced services, products, and businesses. Your stories are always well-researched and well-written, which a lot of readers appreciate. 
In this specific task, you are going to pick a topic to ask the interviewee about. 

Pick a topic with the following criteria:
- The topic should be the most important detail that is missing from the interviewee's response.
- The topic should be something that the interviewee is likely to know about.
- The interviewee would like to talk about the topic since it's what they care about the most.
- The topic should be fit with the current conversation flow.

story: {story}
conversation: {conversation}
missing detail: {missing_detail}
"""
    )

    chain = prompt | chat_model_openai_4o.with_structured_output(
        IsPickedMissingDetailAppropriate
    )

    is_appropriate = chain.invoke(
        {
            "story": documents.review.story,
            "conversation": messages_to_string(
                documents.review.messages[-2:],
                ai_role="journalist",
                user_role="customer",
            ),
            "missing_detail": documents.missing_details.content,
        }
    )
    print("     judgement:", is_appropriate.judgement)

    if is_appropriate.judgement:
        return  n(generate_reply)
    else:
        return "find_missing_details"
