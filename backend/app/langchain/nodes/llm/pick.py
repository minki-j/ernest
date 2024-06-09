from bson import ObjectId
from datetime import datetime
from enum import Enum
import random


from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from app.langchain.schema import Documents
from app.langchain.utils.converters import to_role_content_tuples
from app.langchain.common import llm, chat_model, output_parser, chat_model_openai_4o

from langchain_core.pydantic_v1 import BaseModel, Field

from app.langchain.utils.converters import messages_to_string


class BestTopic(BaseModel):
    """The topic that the customer care about the most."""

    reason: str = Field(description="The reason why the chosen detail is the best.")
    choice: int = Field(description="The index of the best choice.")


def pick_best_missing_detail(state: dict[str, Documents]):
    print("\n==>> pick_best_missing_detail")
    documents = state["documents"]

    prompt = PromptTemplate.from_template(
        """
You are a potential customer seeking recommendations for a reliable vendor to purchase a specific product or service. You are speaking with someone who recently made a purchase from a vendor. Choose a topic to gain insights into their experience. Focus on the aspects that matter most to you, such as product quality, customer service, pricing, delivery time, or overall satisfaction. Keep in mind that you are just a regular customer, not a market researcher, so you should ask questions that are relevant to your needs and preferences.

---
Here are some exmaple:
Latest conversation:
Summarized story:
Options:
reason: 
choice:
___
Now it's your turn

Latest conversation: {conversation}
Summarized story: {story}
Options: {options}
"""
    )

    chain = prompt | chat_model_openai_4o.with_structured_output(BestTopic)

    options = (
        documents.state.missing_details["story_and_reply"]
        + documents.state.missing_details["story_only"]
        + documents.state.missing_details["customer_perspective"]
    )
    print("options:", options)
    indexed_options = "\n".join(f"{i}. {element}" for i, element in enumerate(options))

    best_topic = chain.invoke(
        {
            "story": documents.review.story,
            "conversation": messages_to_string(
                documents.review.messages[-10:], ai_role="you", user_role="customer"
            ),
            "options": indexed_options,
        }
    )

    print("     best missing detail:", options[best_topic.choice])
    print("     reason:", best_topic.reason)

    documents.state.chosen_missing_detail = options[best_topic.choice]

    return {"documents": documents}


class MatchResult(BaseModel):
    """The result of one-on-one match."""

    explanation: str = Field(
        description="Comparison between two options and the reason for the winner."
    )
    winner: int = Field(description="The index of the winner option.")


def random_one_on_one_match(state: dict[str, Documents]):
    print("\n==>> random_one_on_one_match")
    documents = state["documents"]

    prompt = PromptTemplate.from_template(
        """
You are a potential customer seeking recommendations for a reliable vendor to purchase a specific product or service. You are speaking with someone who recently made a purchase from a vendor. There will be two options of questions that you can ask to the person you are speaking with. Compare the two options and choose the one that you think is more relevant to your needs and preferences.
Focus on the aspects that matter most to you, such as product quality, customer service, pricing, delivery time, or overall satisfaction. Keep in mind that you are just a regular customer, not a market researcher, so you should ask questions that are relevant to your needs and preferences.

---
Black List. Don't pick these options:
- About future plans.
- About how the customer's trust has changed.

---
Here are some exmaple:

Summarized story:
Latest conversation:
Options:
explanation: 
winner:
___
Now it's your turn

Summarized story: {story}
Latest conversation: {conversation}
Options: {options}
"""
    )

    chain = prompt | chat_model_openai_4o.with_structured_output(MatchResult)

    options = documents.state.tournament["players"]
    documents.state.tournament["players"] = []

    if len(options) % 2 == 1:
        bye_player = options.pop()
        documents.state.tournament["players"] = [bye_player]
        print("     bye player:", bye_player)

    batch_input = []

    random.shuffle(options)

    for i in range(0, len(options) - 1, 2):
        batch_input.append(
            {
                "story": documents.review.story,
                "conversation": messages_to_string(
                    documents.review.messages[-10:], ai_role="you", user_role="customer"
                ),
                "options": f"0.{options[i]}\n1.{options[i+1]}",
            }
        )

    results = chain.batch(batch_input)
    for idx, result in enumerate(results):
        print("     ----- match ", idx)
        print("     winner:", options[result.winner])
        print(
            "     looser:",
            (
                options[result.winner - 1]
                if result.winner % 2 == 1
                else options[result.winner + 1]
            ),
        print("     explanation:", result.explanation)
    )

    documents.state.tournament["players"] += [
        options[2 * batch_idx - 2 if result.winner % 2 == 0 else 2 * batch_idx - 1]
        for batch_idx, result in enumerate(results)
    ]

    print("     players:", documents.state.tournament["players"])

    return {"documents": documents}
