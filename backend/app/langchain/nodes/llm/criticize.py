from varname import nameof as n
from bson import ObjectId
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from app.langchain.schema import Documents

from app.langchain.common import llm, chat_model, output_parser

from langchain_core.pydantic_v1 import BaseModel, Field

from app.langchain.nodes.llm.generate import generate_reply

def reflection(state: dict[str, Documents]):
    print("\n==>> reflection")
    documents = state["documents"]

    return n(generate_reply)
