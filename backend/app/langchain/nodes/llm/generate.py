from bson import ObjectId
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from app.langchain.schema import Documents
from app.langchain.utils.converters import to_role_content_tuples
from app.langchain.common import llm, chat_model, output_parser

from langchain_core.pydantic_v1 import BaseModel, Field

def generate_reply(state: dict[str, Documents]):
    print("==>> generate_reply")
    documents = state["documents"]

    messages = to_role_content_tuples(documents.review.messages[-8:])
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a counselor listening to a customer who just visited a vet and had a unpleasant experience. Reply with the following instructions and the previous conversation. Reply Instruction: {reply_instruction}",
            ),
            *messages,
        ]
    )

    chain = prompt | chat_model | output_parser

    documents.state.reply_message = chain.invoke(
        {
            "reply_instruction": documents.state.instruction,
        }
    )

    return {"documents": documents}
