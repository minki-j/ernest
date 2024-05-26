from typing import Literal

from app.langchain.schema import Documents
from app.schemas.schemas import State
from bson import ObjectId
from datetime import datetime

from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from app.langchain.schema import Documents

from app.langchain.common import llm, chat_model, output_parser

from langchain_core.pydantic_v1 import BaseModel, Field

from enum import Enum
from bson import ObjectId
from datetime import datetime

from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from dspy.predict.langchain import LangChainPredict, LangChainModule

from app.langchain.schema import Documents

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


def is_reply_A_to_Q(Documents: Documents):

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
            "question": Documents["messages"][-2]["content"],
            "reply": Documents["messages"][-1]["content"],
            "options": "question, reply, other",
        }
    )

    print("Intent: ", result.intent.value)

    if (
        result.intent == Intents.REPLY
        and Documents["ephemeral"]["relevant_question_idx"] is not None
    ):
        return "evaluate_enoughness_score"
    elif (
        result.intent == Intents.REPLY
        and Documents["ephemeral"]["relevant_question_idx"] is None
    ):
        return "fork1"
    elif result.intent == Intents.QUESTION:
        return "generate_reply_for_not_A"
    else:  # Intents.OTHER
        return "__end__"


class Intents(str, Enum):
    """Enumeration for single-label intent classification."""

    REPLY = "reply"
    QUESTION = "question"
    OTHER = "other"


class ReplyIntent(BaseModel):
    """Get the intent of the reply among the given options"""

    intent: Intents = Field(description="The intent of the reply")


def is_reply_A_to_Q(Documents: Documents):

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
            "question": Documents["messages"][-2]["content"],
            "reply": Documents["messages"][-1]["content"],
            "options": "question, reply, other",
        }
    )

    print("Intent: ", result.intent.value)

    if (
        result.intent == Intents.REPLY
        and Documents["ephemeral"]["relevant_question_idx"] is not None
    ):
        return "evaluate_enoughness_score"
    elif (
        result.intent == Intents.REPLY
        and Documents["ephemeral"]["relevant_question_idx"] is None
    ):
        return "fork1"
    elif result.intent == Intents.QUESTION:
        return "generate_reply_for_not_A"
    else:  # Intents.OTHER
        return "__end__"


def decide_to_pick_new_question(
    documents: dict[str, Documents],
) -> Literal["generate_answer_with_new_msg", "decide_next_question"]:
    print("\n==>> decide_to_pick_new_question")
    # becareful to not use boolean comparison here since index 0 is False
    if documents["ephemeral"]["relevant_question_idx"] is None:
        print("-> decide_next_question")
        return "decide_next_question"
    else:
        print("-> generate_answer_with_new_msg -> check_enoughness_score")
        return "generate_answer_with_new_msg"


def decide_enoughness_threshold(
    Documents: Documents,
) -> Literal["decide_next_question", "generate_new_q_for_current_topic"]:
    print("\n==>> decide_enoughness_threshold")
    current_topic_idx = Documents["ephemeral"]["current_topic_idx"]
    relevant_question_idx = Documents["ephemeral"]["relevant_question_idx"]
    enoughness_score = Documents["topics"][current_topic_idx]["questions"][
        relevant_question_idx
    ]["enough"]

    if enoughness_score < Documents["ephemeral"]["enoughness_threshold"]:
        return "generate_new_q_for_current_topic"
    else:
        return "decide_next_question"


def is_next_Q(Documents: Documents) -> Literal["generate_answer_with_new_msg", "decide_next_question"]:
    print("\n==>> is_next_Q")

    current_topic_idx = Documents["ephemeral"]["current_topic_idx"]

    questions = Documents["topics"][current_topic_idx]["questions"]

    questions_lower_than_threshold = [
        q for q in questions if q["enough"] < Documents["ephemeral"]["enoughness_threshold"]
    ]

    if len(questions_lower_than_threshold) == 0:
        return "fork2"
    else:
        return "pick_next_Q"
