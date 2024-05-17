from bson import ObjectId
from datetime import datetime

from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from dspy.predict.langchain import LangChainPredict, LangChainModule

from app.langchain.states.document_state import DocumentState
from app.langchain.utils.messages_to_string import (
    messages_to_string,
    messages_to_chatPromptTemplate,
)
from app.langchain.common import llm, chat_model, output_parser

from langchain_core.pydantic_v1 import BaseModel, Field

from enum import Enum


class Intents(str, Enum):
    """Enumeration for single-label intent classification."""

    REPLY = "reply"
    QUESTION = "question"
    OTHER = "other"


class ReplyIntent(BaseModel):
    """Get the intent of the reply among the given options"""
    intent: Intents = Field(description="The intent of the reply")


def is_reply_A_to_Q(documentState: DocumentState):

    prompt = PromptTemplate.from_template(
        """You are a reply intent classifier. Pick the intent of the given text. Your reply should be a few words long. 

        Here are examples:

        question: Who was your favorite speaker and why?
        reply: I liked the speaker who talked about the new technologies. He was very informative.
        options: question, reply, other
        intent: reply

        question: Did you find the venue easily?
        reply: How many questions are there left?
        options: question, reply, other
        intent: question

        question: How many new people did you meet at the meetup?
        reply: Hey Alison! Nice to meet you today. I'm John.
        options: question, reply, other
        intent: other

        Now, it's your turn. What is the intent of the given text? 

        question: {question}
        reply: {reply}
        options: {options}
        intent:
"""
    )

    chain = prompt | chat_model.with_structured_output(ReplyIntent)

    result = chain.invoke(
        {
            "question": documentState["messages"][-2]["content"],
            "reply": documentState["messages"][-1]["content"],
            "options": "question, reply, other",
        }
    )

    print("Intent: ", result.intent.value)

    if result.intent == Intents.REPLY and documentState["ephemeral"]["relevant_question_idx"] is not None:
        return "evaluate_enoughness_score"
    elif result.intent == Intents.REPLY and documentState["ephemeral"]["relevant_question_idx"] is None:
        return "fork1"
    elif result.intent == Intents.QUESTION:
        return "generate_reply_for_not_A"
    else: # Intents.OTHER
        return "__end__"
