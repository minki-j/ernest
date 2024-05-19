from bson import ObjectId
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from dspy.predict.langchain import LangChainPredict, LangChainModule

from app.langchain.common import Documents
from app.langchain.utils.messages_to_string import (
    messages_to_string,
    messages_to_chatPromptTemplate,
)
from app.langchain.common import llm, chat_model, output_parser

from langchain_core.pydantic_v1 import BaseModel, Field

def end_conversation(state: dict[str, Documents]):
    print("==>> end_conversation")
    documents = state["documents"]

    documents.state.reply_message = "Thank you for your time. Have a great day!"

    return {"documents": documents}

def ask_name(state: dict[str, Documents]):
    print("==>> ask_name")
    documents = state["documents"]

    message = "Hi I'm Ernest! What's your name?"

    documents.state.reply_message = message

    return {"documents": documents}

def greeting(state: dict[str, Documents]):
    print("==>> greeting")
    documents = state["documents"]

    first_msg_from_ai = f"Hi {documents.user.name}! What's up?"

    documents.state.reply_message = first_msg_from_ai

    return {"documents": documents}

def generate_reply(state: dict[str, Documents]):
    print("==>> generate_reply")
    documents = state["documents"]

    # system_message = "reply to the user. response the last message of the user and ask the next question naturally. the next question is the following: {next_question}"

    # messages = messages_to_chatPromptTemplate(documents["messages"][-6:])

    # prompt = ChatPromptTemplate.from_messages(
    #     [
    #         ("system", system_message),
    #         *messages,
    #     ]
    # )

    # chain = prompt | chat_model | output_parser
    # reply = chain.invoke(
    #     {
    #         "next_question": documents["ephemeral"]["next_question"],
    #     }
    # )

    # documents["ephemeral"]["reply_message"] = reply
    # message_id = ObjectId()
    # documents["messages"].append(
    #     {
    #         "id": message_id,
    #         "role": "ai",
    #         "content": reply,
    #         "created_at": datetime.now().isoformat(),
    #     }
    # )

    # # update the reference_message_ids of the relevant question
    # # first check if there is a next question
    # relevant_question_idx = documents["ephemeral"].get("next_question_idx", None)

    # # if not found, check the relevant question
    # if relevant_question_idx is None:
    #     relevant_question_idx = documents["ephemeral"].get(
    #         "relevant_question_idx", None
    #     )

    # if relevant_question_idx is not None:
    #     documents["topics"][current_topic_idx]["questions"][
    #         relevant_question_idx
    #     ].setdefault("reference_message_ids", []).append(message_id)

    return {"documents": documents}


def greeting(state: dict[str, Documents]):
    print("==>> greeting")
    documents = state["documents"]

    first_msg_from_ai = f"Hi {documents.user.name}! What's up?"

    documents.state.reply_message = first_msg_from_ai

    return {"documents": documents}




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
            "last_4_messages": messages_to_string(Documents["messages"][-4:]),
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
