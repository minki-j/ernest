from bson import ObjectId
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from app.langchain.schema import Documents
from app.langchain.utils.converters import messages_to_string

from app.langchain.common import llm, chat_model, output_parser

from langchain_core.pydantic_v1 import BaseModel, Field


class Instruction(BaseModel):
    """A planned instruction for the next reply of a chat message."""

    content: str


def plan_instruction(state: dict[str, Documents]):
    print("==>> plan_instruction")
    documents = state["documents"]

    print("context:", documents.state.context)

    prompt = f"""
You are an helpful AI assistant planning an instruction for the next reply of a chat message. With the user info, vendor info and previous conversation, please plan an instruction for the next reply.

User info: {documents.state.context["user_info"]}
Vendor info: {documents.state.context["vendor_info"]}
previous conversation: {messages_to_string(documents.review.messages[-10:])}
"""
    result = chat_model.with_structured_output(Instruction).invoke(prompt)

    documents.state.instruction = result.content

    return {"documents": documents}
