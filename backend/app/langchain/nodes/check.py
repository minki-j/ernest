from typing import Literal

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field

from app.langchain.common import Documents
from app.schemas.schemas import State, Role, Message

from app.langchain.common import llm, chat_model, output_parser

def find_relevant_report(state: dict[str, Documents]):
    print("==>> find_relevant_report")
    documents = state["documents"]

    return {"documents": documents}

def find_to_update(state: dict[str, Documents]):
    print("==>> find_to_update")
    documents = state["documents"]

    return {"documents": documents}