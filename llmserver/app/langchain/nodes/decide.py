from bson import ObjectId
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from dspy.predict.langchain import LangChainPredict, LangChainModule

from app.langchain.common import Documents
from app.langchain.utils.messages_to_string import messages_to_string
from app.langchain.common import llm, chat_model, output_parser

from bson import ObjectId
from datetime import datetime
from typing import Literal

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from dspy.predict.langchain import LangChainPredict, LangChainModule

from app.langchain.common import Documents
from app.langchain.utils.messages_to_string import messages_to_string
from app.langchain.common import llm, chat_model, output_parser


def decide_next_question(Documents: Documents):
    print("==>> decide_next_question")
    current_topic_idx = Documents["ephemeral"]["current_topic_idx"]

    unasked_questions = []
    for question in Documents["topics"][current_topic_idx]["questions"]:
        if (
            question.setdefault("enough", 0)
            < Documents["ephemeral"]["enoughness_threshold"]
        ):
            unasked_questions.append(question["content"])

    if len(unasked_questions) == 0:
        if not Documents["ephemeral"]["current_topic_idx"] == len(
            Documents["topics"]
        ):
            current_topic_idx += 1
            Documents["ephemeral"]["current_topic_idx"] = current_topic_idx
        else:
            current_topic_idx = -1
            Documents["ephemeral"]["current_topic_idx"] = current_topic_idx

    # if there is no more topics to ask, then skip this node
    if current_topic_idx < 0:
        return Documents

    recent_messages = messages_to_string(Documents["messages"][-4:])
    options = " / ".join(unasked_questions)

    # todo: if the options are empty, then create a new question. Need a separate prompt for this task
    # todo: Add "asked question list" and "purpose of survey".
    # if len(options) == 0:
    #     prompt = PromptTemplate.from_template(
    #         """
    #    You are a survey bot generating the next question based on the current conversation flow and already asked questions.
    #     """
    #     )
    #     return Documents

    # todo: make sure that the ai doesn't create a new question that is not in the options.
    prompt = PromptTemplate.from_template(
        """
You are a survey bot picking the next question based on the current conversation flow. Don't create a new question that is not in the options.
You'll be provided with the last 4 messages and the list of unasked questions. Choose the next question from the option if the options are provided. If the options are empty then create a new question. Here are examples:
---
Examples:

last 4 messages: ai: How are you? / user: I'm good. / ai: What's your favorite color? / user: Blue.
options: What's your favorite food? / What's your dream
next_question: What's your favorite food?

last 4 messages: ai: when did you marry? / user: I married in 2020. / ai: How many children do you have? / user: I have 2 children.
options: what does KDINW stand for?
next_question: what does KDINW stand for?

last 4 messages: ai: What's your best memory? / user: My best memory is when I went to the beach with my family. / ai: What's your favorite food? / user: My favorite food is pizza.
options:
next_question: What's your favorite country?
---
Now it's your turn to pick the next question. Here is the information you need:
last 4 messages: {recent_messages}
options: {options}
next_question:
"""
    )

    # todo: change it to a structured output
    chain = prompt | llm | output_parser
    result = chain.invoke({"recent_messages": recent_messages, "options": options})
    result = result.strip()
    print(f"next_question: {result} / out of the options: {options}")

    next_question_idx = None
    for idx, question in enumerate(
        Documents["topics"][current_topic_idx]["questions"]
    ):
        # todo: instead of a hard comparison, use a similarity measure
        if question["content"].strip() == result:
            next_question_idx = idx
            break

    # add question to Documents if it's new
    if next_question_idx is None:
        next_question_idx = len(Documents["topics"][current_topic_idx]["questions"])
        Documents["questions"].append(
            {
                "id": ObjectId(),
                "content": result,
                "created_at": datetime.now().isoformat(),
            }
        )
    print("next_question_idx: ", next_question_idx)
    Documents["ephemeral"]["next_question"] = result
    Documents["ephemeral"]["next_question_idx"] = next_question_idx

    return Documents


def decide_whether_to_move_to_next_topic(Documents: Documents):
    print("==>> decide_whether_to_move_to_next_topic")
    current_topic_idx = Documents["ephemeral"]["current_topic_idx"]

    unasked_questions = []
    for question in Documents["topics"][current_topic_idx]["questions"]:
        if (
            question.setdefault("enough", 0)
            < Documents["ephemeral"]["enoughness_threshold"]
        ):
            unasked_questions.append(question["content"])

    if len(unasked_questions) == 0:
        if not Documents["ephemeral"]["current_topic_idx"] == len(
            Documents["topics"]
        ):
            Documents["ephemeral"]["current_topic_idx"] += 1
        else:
            Documents["ephemeral"]["current_topic_idx"] = -1
    
    return Documents
