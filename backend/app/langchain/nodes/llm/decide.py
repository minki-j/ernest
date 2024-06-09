from varname import nameof as n
from enum import Enum
from bson import ObjectId
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from app.langchain.schema import Documents, StateItem, Bio
from app.langchain.utils.converters import messages_to_string

from app.langchain.common import llm, chat_model, output_parser, chat_model_openai_4o

from langchain_core.pydantic_v1 import BaseModel, Field


class ReplyType(Enum):
    reaction_only = "reaction_only"
    question_only = "question_only"
    reaction_and_question = "reaction_and_question"

class DecideReplyType(BaseModel):
    """The type of reply the customer has given in the interview."""

    reason: str = Field(description="The reason why the chosen type is the best.")
    type: ReplyType = Field(description="The type of reply the journalist will give.")


# ! This doesn't work well. It always returns reaction_and_question. Unreliably returns reaction_only.
def decide_reply_type(state: dict[str, Documents]):
    print("\n==>> decide_reply_type")
    documents = state["documents"]

    prompt = PromptTemplate.from_template(
        """
        As a seasoned journalist with 40+ years of experience at a prestigious magazine, you specialize in customer experience with services, products, and businesses. Your stories are always thoroughly researched and well-written, a fact well-appreciated by many readers.
        In the upcoming task, you will need to decide whether to merely respond to the customer's reply, solely ask questions without any reaction, or both respond and ask questions. Consider the context of the message and choose the most natural one.

        Tip: When the user's last message seems like that the user will continue explaining about the detail, just react only without asking a new question. 
        
        previous conversation: {conversation}
        possible reaction from the journalist: {possible_reaction}
        possible question from the journalist: {possible_question}
        """
    )

    chain = prompt | chat_model_openai_4o.with_structured_output(DecideReplyType)

    reply_type = chain.invoke(
        {
            "conversation": messages_to_string(
                documents.review.messages[-10:],
                ai_role="journalist",
                user_role="customer",
            ),
            "possible_reaction": documents.state.candidate_reply_message.reaction,
            "possible_question": documents.state.candidate_reply_message.question,
        }
    )
    print("    reply_type:", reply_type.type.value)

    if reply_type.type == ReplyType.reaction_only:
        documents.state.reply_message = documents.state.candidate_reply_message.reaction
    elif reply_type.type == ReplyType.question_only:
        documents.state.reply_message = documents.state.candidate_reply_message.question
    elif reply_type.type == ReplyType.reaction_and_question:
        documents.state.reply_message = f"{documents.state.candidate_reply_message.reaction} {documents.state.candidate_reply_message.question}"

    return {"documents": documents}
