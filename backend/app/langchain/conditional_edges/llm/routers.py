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


from app.langchain.common import llm, chat_model, output_parser

from langchain_core.pydantic_v1 import BaseModel, Field


class IsPlannedEnough(BaseModel):
    """Return true if the planned instruction is good enough. Otherwise, return false."""

    answer: bool