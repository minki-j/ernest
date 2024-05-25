from bson import ObjectId
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from app.langchain.schema import Documents
from app.langchain.utils.converters import to_role_content_tuples
from app.langchain.common import llm, chat_model, output_parser, chat_model_openai_4o

from langchain_core.pydantic_v1 import BaseModel, Field

def generate_reply(state: dict[str, Documents]):
    print("==>> generate_reply")
    documents = state["documents"]
    print("    reply_instruction:", documents.state.instruction)

    messages = to_role_content_tuples(documents.review.messages[-8:])
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are a counselor listening to a customer who just visited a vet and had a unpleasant experience. You are not a part of any vet, so you don't have to defend them or try to assit or resolve the issue. Just listen to the customer's experience, validate their feelings and gather more information about the problem. Keep a friendly tone and show empathy. Be on customer's side.

Your reply will be primed by a instruction. Here are some examples:

Instruction: Agree with the customer and blame the vet, then ask if they 


For this specific conversation scenario, follow this instruction: {reply_instruction}""",
            ),
            *messages,
        ]
    )

    chain = prompt | chat_model_openai_4o | output_parser

    documents.state.reply_message = chain.invoke(
        {
            "reply_instruction": documents.state.instruction,
        }
    )

    return {"documents": documents}
