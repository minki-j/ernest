from langchain_openai import ChatOpenAI, OpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.graph import END, MessageGraph, StateGraph
from bson import ObjectId
from dspy.predict.langchain import LangChainPredict, LangChainModule
from app.langchain.states.document_state import DocumentState
from app.langchain.utils.messages_to_string import (
    messages_to_string,
    messages_to_chatPromptTemplate,
)
from langgraph.prebuilt import ToolNode
from typing import Literal
from datetime import datetime
import os

output_parser = StrOutputParser()
# model = ChatOpenAI(model="gpt-3.5-turbo")
model = ChatAnthropic(model="claude-3-haiku-20240307")
llm = OpenAI()

# Features to add
# todo: export the report of the survey
# todo: Add purpose of the survey
# todo: Add quantitaive version of question
# todo: conceal PII when asked
# todo: discard previous answer when asked
# todo: add local llama3 model

def check_relevant_question(documentState: DocumentState):
    print("==>> check_relevant_question")
    id_of_last_bot_message = None
    for msg in reversed(documentState["messages"]):
        if msg["role"] == "ai":
            id_of_last_bot_message = msg["id"]
            break

    relevant_question = None
    relevant_question_idx = None
    if id_of_last_bot_message:
        for idx, question in enumerate(documentState["questions"]):
            if id_of_last_bot_message in question.get("reference_message_ids", []):
                relevant_question = question
                relevant_question_idx = idx
                break
    print("relevant_question_idx: ", relevant_question_idx)

    if relevant_question:
        documentState["questions"][relevant_question_idx].setdefault(
            "reference_message_ids", []
        ).append(documentState["messages"][-1]["id"])
    documentState["ephemeral"]["relevant_question_idx"] = relevant_question_idx

    return documentState


def need_to_pick_new_question(
    documentState: DocumentState,
) -> Literal["update_answer", "pick_next_question"]:
    print("==>> need_to_pick_new_question")
    # becareful to not use boolean comparison here since index 0 is False
    if documentState["ephemeral"]["relevant_question_idx"] is None:
        print("NO -> pick_next_question")
        return "pick_next_question"
    else:
        print("YES -> update_answer -> check_enoughness_score")
        return "update_answer"

# todo: when user's answer can be added to other questions than the current one, we need to update the answer for that question as well. --> Solution: embed the question+answers in the latent space and aggregate nearest neighbors.
def update_answer(documentState: DocumentState):
    if documentState["messages"][-1]["content"].lower() == "pass":
        return documentState
    
    print("==>> update_answer")
    relevant_question_idx = documentState["ephemeral"]["relevant_question_idx"]
    question_content = documentState["questions"][relevant_question_idx]["content"]
    original_answer = documentState["questions"][relevant_question_idx].get(
        "answer", "not answered yet."
    )

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
    #todo: if the user's last message is not related to the question, then keep the previous answer as an updated answer.

    prompt = prompt.format(
        question_content=question_content,
        original_answer=original_answer,
        user_message=documentState["messages"][-1]["content"],
    )

    #todo: make this step robust. The answer could be replaced to an error message
    updated_answer = llm.invoke(prompt)
    updated_answer = updated_answer.strip().split("\n")[0]
    print(f"updated_answer: {updated_answer}")

    documentState["questions"][relevant_question_idx]["answer"] = updated_answer

    return documentState


def check_enoughness_score(documentState: DocumentState):
    print("==>> check_enoughness_score")

    relevant_question_idx = documentState["ephemeral"]["relevant_question_idx"]

    if documentState["messages"][-1]["content"].lower() == "pass":
        documentState["questions"][relevant_question_idx]["enough"] = 1.0
        return documentState

    prompt = PromptTemplate.from_template(
        #todo: Improve this inference so that it returns more accurate scores. We need a good set of few shots.
        """Check if the answer is enough for the question. The score should be in range of 0 and 1. Here are examples:
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
        Now it's your turn to check the enoughness score. Here is the information you need:
        question: {question}
        answer: {answer}
        enoughness_score:"""
    )
    relevant_question = documentState["questions"][relevant_question_idx]
    prompt = prompt.format(
        question=relevant_question["content"], answer=relevant_question["answer"]
    )
    enoughness_score = llm.invoke(prompt)
    enoughness_score = enoughness_score.strip().split("\n")[0]
    print(f"enoughness_score: ", enoughness_score)

    documentState["questions"][relevant_question_idx]["enough"] = float(
        enoughness_score.strip().split("\n")[0]
    )

    return documentState


def is_enoughness_higher_than_threshold(
    documentState: DocumentState,
) -> Literal["pick_next_question", "ask_more_about_current_topic"]:
    print("==>> is_enoughness_higher_than_threshold")
    relevant_question_idx = documentState["ephemeral"]["relevant_question_idx"]
    enoughness_score = documentState["questions"][relevant_question_idx]["enough"]

    if enoughness_score < documentState["ephemeral"]["enoughness_threshold"]:
        return "ask_more_about_current_topic"
    else:
        return "pick_next_question"


def pick_next_question(documentState: DocumentState):
    print("==>> pick_next_question")
    unasked_questions = []
    for question in documentState["questions"]:
        if (
            question.setdefault("enough", 0)
            < documentState["ephemeral"]["enoughness_threshold"]
        ):
            unasked_questions.append(question["content"])

    recent_messages = messages_to_string(documentState["messages"][-4:])
    options = " / ".join(unasked_questions)

    # todo: if the options are empty, then create a new question. Need a separate prompt for this task
    # todo: Add "asked question list" and "purpose of survey".
    # if len(options) == 0:
    #     prompt = PromptTemplate.from_template(
    #         """
    #    You are a survey bot generating the next question based on the current conversation flow and already asked questions.
    #     """
    #     )
    #     return documentState

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

    # todo: change it to a structed output
    chain = prompt | llm | output_parser
    result = chain.invoke({"recent_messages": recent_messages, "options": options})
    result = result.strip()
    print(f"next_question: {result} / out of the options: {options}")

    next_question_idx = None
    for idx, question in enumerate(documentState["questions"]):
        # todo: instead of hard comparison, use a similarity measure
        if question["content"].strip() == result:
            next_question_idx = idx
            break

    # add question to documentState if it's new
    if next_question_idx is None:
        next_question_idx = len(documentState["questions"])
        documentState["questions"].append(
            {
                "id": ObjectId(),
                "content": result,
                "created_at": datetime.now().isoformat(),
            }
        )
    print("next_question_idx: ", next_question_idx)
    documentState["ephemeral"]["next_question"] = result
    documentState["ephemeral"]["next_question_idx"] = next_question_idx

    return documentState


def ask_more_about_current_topic(documentState: DocumentState):
    relevant_question_idx = documentState["ephemeral"]["relevant_question_idx"]
    relevant_question = documentState["questions"][relevant_question_idx]

    #todo: add examples
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
            "last_4_messages": messages_to_string(documentState["messages"][-4:]),
        }
    )

    print(f"next_question: {next_question}")

    documentState["ephemeral"]["next_question"] = next_question

    return documentState


def generate_reply(documentState: DocumentState):
    print("==>> generate_reply")

    next_question = documentState["ephemeral"].get("next_question", None)
    system_message = "reply to the user. response the last message of the user and ask the next question naturally. the next question is the following: {next_question}"
    if not next_question:
        reply = "All of the survey questions are answered. Thank you for your time. Have a great day!"
        documentState["ephemeral"]["message"] = reply
        documentState["messages"].append(
            {
                "id": ObjectId(),
                "role": "ai",
                "content": reply,
                "created_at": datetime.now().isoformat(),
            }
        )
        return documentState

    messages = messages_to_chatPromptTemplate(documentState["messages"][-4:])
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_message),
            *messages,
        ]
    )

    chain = prompt | model | output_parser
    reply = chain.invoke({"next_question": next_question})

    documentState["ephemeral"]["message"] = reply
    message_id = ObjectId()
    documentState["messages"].append(
        {
            "id": message_id,
            "role": "ai",
            "content": reply,
            "created_at": datetime.now().isoformat(),
        }
    )

    relevant_question_id = documentState["ephemeral"].get("next_question_idx", None)

    # Becareful to not use boolean comparison here sine index 0 is False
    if relevant_question_id is None:
        relevant_question_id = documentState["ephemeral"].get(
            "relevant_question_idx", None
        )

    if relevant_question_id is not None:
        documentState["questions"][relevant_question_id].setdefault(
            "reference_message_ids", []
        ).append(message_id)

    return documentState


# Flow engineering
# 1. if there is no previous conversation or no relevant question
#     1.1 pick a question from the list (tool)
# 2. if a relevant question exists
#     2.2 update the answer with user's last message
#     2.3 check if the answer is enough
#         2.3.1 if not enough, ask more questions about the current topic
#         2.3.2 if enough, choose the next question
graph = StateGraph(DocumentState)

graph.add_node("check_relevant_question", check_relevant_question)
graph.add_conditional_edges("check_relevant_question", need_to_pick_new_question)

graph.add_node("update_answer", update_answer)
graph.add_edge("update_answer", "check_enoughness_score")

graph.add_node("check_enoughness_score", check_enoughness_score)
graph.add_conditional_edges(
    "check_enoughness_score", is_enoughness_higher_than_threshold
)

graph.add_node("pick_next_question", pick_next_question)
graph.add_edge("pick_next_question", "generate_reply")

graph.add_node("ask_more_about_current_topic", ask_more_about_current_topic)
graph.add_edge("ask_more_about_current_topic", "generate_reply")

graph.add_node("generate_reply", generate_reply)
graph.add_edge("generate_reply", END)

graph.set_entry_point("check_relevant_question")
langgraph_app = graph.compile()
