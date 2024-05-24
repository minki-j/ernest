from bson import ObjectId
from datetime import datetime

from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from app.langchain.common import llm, chat_model, output_parser
from app.langchain.schema import Documents


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
        if not Documents["ephemeral"]["current_topic_idx"] == len(Documents["topics"]):
            current_topic_idx += 1
            Documents["ephemeral"]["current_topic_idx"] = current_topic_idx
        else:
            current_topic_idx = -1
            Documents["ephemeral"]["current_topic_idx"] = current_topic_idx

    # if there is no more topics to ask, then skip this node
    if current_topic_idx < 0:
        return Documents

    recent_messages = ""
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
    for idx, question in enumerate(Documents["topics"][current_topic_idx]["questions"]):
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
        if not Documents["ephemeral"]["current_topic_idx"] == len(Documents["topics"]):
            Documents["ephemeral"]["current_topic_idx"] += 1
        else:
            Documents["ephemeral"]["current_topic_idx"] = -1

    return Documents


class EnoughnessScore(BaseModel):
    """Get the enoughness score of the answer to the question"""

    enoughness_score: float = Field(
        description="The enoughness score of the answer to the question. Range is between 0 and 1."
    )


def evaluate_enoughness_score(Documents: Documents):
    print("==>> generate_enoughness_score")

    relevant_question_idx = Documents["ephemeral"]["relevant_question_idx"]
    current_topic_idx = Documents["ephemeral"]["current_topic_idx"]

    if Documents["messages"][-1]["content"].lower() == "pass":
        Documents["topics"][current_topic_idx]["questions"][relevant_question_idx][
            "enough"
        ] = 1.0
        return Documents

    prompt = PromptTemplate.from_template(
        # todo: Improve this inference so that it returns more accurate scores. We need a good set of few shots.
        """examine if the answer is enough for the question. The score should be in range of 0 and 1. Here are examples:
        Question: What is your favorite color and why?
        Answer: My favorite color is blue.
        enoughness_score: 0.5
        ---
        Question: What kind of sports do you like?
        Answer: I don't like sports
        enoughness_score: 1.0
        ---
        Question: Why do you like to go on a hike?
        Answer: It's because I love nature.
        enoughness_score: 0.6
        ---
        Now it's your turn to examine the enoughness score. Here is the information you need:
        question: {question}
        answer: {answer}
        enoughness_score:"""
    )
    relevant_question = Documents["topics"][current_topic_idx]["questions"][
        relevant_question_idx
    ]
    prompt = prompt.format(
        question=relevant_question["content"], answer=relevant_question["answer"]
    )
    result = llm.with_structured_output(EnoughnessScore).invoke(prompt)
    enoughness_score = result.enoughness_score
    print(f"enoughness_score: ", enoughness_score)

    Documents["topics"][current_topic_idx]["questions"][relevant_question_idx][
        "enough"
    ] = float(enoughness_score.strip().split("\n")[0])

    return Documents


# todo: user's answer can be related to other questions than the current one. (having MECE topics reduces the scope of this problem)
def generate_answer_with_new_msg(Documents: Documents):
    if Documents["messages"][-1]["content"].lower() == "pass":
        return Documents

    print("==>> generate_answer_with_new_msg")
    current_topic_idx = Documents["ephemeral"]["current_topic_idx"]
    relevant_question_idx = Documents["ephemeral"]["relevant_question_idx"]
    question_content = Documents["topics"][current_topic_idx]["questions"][
        relevant_question_idx
    ]["content"]
    original_answer = Documents["topics"][current_topic_idx]["questions"][
        relevant_question_idx
    ].get("answer", "not answered yet.")

    prompt = PromptTemplate.from_template(
        """
You are an interviewer tasked with collecting responses to specific questions. You've already received answers from the interviewee and condensed them into a "previous answer". Your goal is to incorporate the new message into the existing answer, thereby creating an "updated answer". Here are examples:\n
---\n
Question: how was the assignments of the course?\n
Previous Answer: It was too much for me.\n
User's Last Message: I mean, there were 3 assignment in total every week and it took 3 hours to complete. I think it was too much for me. Also, the deadline was too short. And some of the assignments were too messy and not clearly explained.\n
Updated Answer: The workload was overwhelming with three assignments each week, each requiring three hours to complete and with tight deadlines. Moreover, some of the assignments were disorganized and lacked clear instructions.\n
---\n
Now it's your turn to update the answer. Here is the information you need. If the user's last message is not related to the question, then keep the previous answer as an updated answer. \n
---\n
Question: {question_content}\n
Previous Answer: {original_answer}\n
User's Last Message: {user_message}\n
Updated Answer:
"""
    )
    # todo: if the user's last message is not related to the question, then keep the previous answer as an updated answer.

    prompt = prompt.format(
        question_content=question_content,
        original_answer=original_answer,
        user_message=Documents["messages"][-1]["content"],
    )

    # todo: make this step robust. The answer could be replaced to an error message
    updated_answer = llm.invoke(prompt)
    updated_answer = updated_answer.strip().split("\n")[0]
    print(f"updated_answer: {updated_answer}")

    Documents["topics"][current_topic_idx]["questions"][relevant_question_idx][
        "answer"
    ] = updated_answer

    return Documents


def generate_new_q_for_current_topic(Documents: Documents):
    relevant_question_idx = Documents["ephemeral"]["relevant_question_idx"]
    relevant_question = Documents["questions"][relevant_question_idx]

    # todo: add examples
    prompt = PromptTemplate.from_template(
        """
Ask more questions about the current question based on the user's last message and the current answer.

question: {question}
answer: {answer}
last 4 messages: {last_4_messages}
next_question:
"""
    )

    chain = prompt | llm | output_parser
    next_question = chain.invoke(
        {
            "question": relevant_question["content"],
            "answer": relevant_question["answer"],
            "last_4_messages": "",
        }
    )

    print(f"next_question: {next_question}")

    Documents["ephemeral"]["next_question"] = next_question

    return Documents


def generate_reply_for_not_A(Documents: Documents):
    print("==>> generate_reply_for_not_A")

    reply = "Answering the questions not related to survey will be added soon, but not available at the moment. Thank you for your patience. Have a great day!"
    Documents["ephemeral"]["reply_message"] = reply
    Documents["messages"].append(
        {
            "id": ObjectId(),
            "role": "ai",
            "content": reply,
            "created_at": datetime.now().isoformat(),
        }
    )

    return Documents
