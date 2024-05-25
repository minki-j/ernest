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
from app.langchain.subgraphs.middle_of_chat.plan_instruction.graph import plan_instruction

from app.langchain.common import llm, chat_model, output_parser

from langchain_core.pydantic_v1 import BaseModel, Field


class IsPlannedEnough(BaseModel):
    """Return true if the planned instruction is good enough. Otherwise, return false."""

    answer: bool


def moc_router(state: dict[str, Documents]):
    print("==>> moc_router")
    documents = state["documents"]

    # If no context, gather context first
    if hasattr(documents.state, "context") is False:
        return n(gather_context)

    # If criticizm exists, decide whether it requires to gather more context or not
    # The criticizm state will be emptied after one loop.
    if hasattr(documents.state, "criticizm"):
        if documents.state.criticizm["requires_context"]:
            return n(gather_context)
        else:
            return n(plan_instruction)

    # Decide whether the planed instruction is good enough. If not, gather more context and plan again.
    prompt = PromptTemplate.from_template(
        """
You are an helpful AI assistant judging whether the planned instruction for a reply of a chat message is good enough. 

previous conversation: {conversation}
planned instruction for the next reply: {planned_instruction}"""
    )

    chain = prompt | chat_model.with_structured_output(IsPlannedEnough)

    is_planned_enough = chain.invoke({"conversation": messages_to_string(documents.review.messages[-10:]), "planned_instruction": documents.state.instruction})

    print('    is_planned_enough:', is_planned_enough.answer)

    if is_planned_enough.answer:
        return "end_router"
    else:
        return n(gather_context)
