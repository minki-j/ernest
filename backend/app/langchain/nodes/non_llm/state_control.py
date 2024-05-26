from bson import ObjectId
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from dspy.predict.langchain import LangChainPredict, LangChainModule

from app.langchain.schema import Documents

from app.langchain.common import llm, chat_model, output_parser
from app.schemas.schemas import Role, Message

from langchain_core.pydantic_v1 import BaseModel, Field


def sync_state_and_doc(state: dict[str, Documents]):
    print("\n==>> sync_state_and_doc")
    documents = state["documents"]

    documents.add(
        Message(
            role=Role.AI,
            content=documents.state.reply_message,
        )
    )

    return {"documents": documents}
