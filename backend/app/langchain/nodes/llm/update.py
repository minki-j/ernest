from typing import Literal

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field

from app.langchain.schema import Documents
from app.schemas.schemas import State, Role, Message

from app.langchain.common import llm, chat_model, output_parser
