from bson import ObjectId
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from app.schemas.schemas import StateItem
from app.langchain.schema import Documents
from app.langchain.utils.converters import to_role_content_tuples
from app.langchain.common import llm, chat_model, output_parser, chat_model_openai_4o

from langchain_core.pydantic_v1 import BaseModel, Field
from app.langchain.utils.converters import messages_to_string


class MissingDetail(BaseModel):
    """A missing detail that the journalist should ask"""

    content: str = Field(description="The content of the detail.")


def find_missing_detail_with_reply(state: dict[str, Documents]):
    print("\n==>> find_missing_detail_with_reply")
    documents = state["documents"]

    prompt = PromptTemplate.from_template(
        """
You are helping a journalist at a famous magazine with 40+ years of experience. The reporter's main area of topic is about how customers experienced services, products, and businesses. Her stories are always well-researched and well-written, which a lot of readers appreciate. 
In this specific task, you are going to assist the journalist by finding missing details from the interviewee's response. Once you provide the missing detail, the journalist will ask the interviewee about it.

Here are some examples:

previous story: The customer went to a restaurant and ordered a steak. The steak was overcooked and the customer was not happy.
recent reply: (journalist) Did you ask the waiter to cook it less? (customer) Yes, I did. I emphasized that I wanted it medium-rare. Can't believe that this happened to this kind of high-end restaurant.
missing detail: The customer said it's a high-end restaurant, but the exact price range of the restaurant is not mentioned.

previoud story: The customer went to a car dealership and bought a car. The customer was happy with the car, but the customer service was not good.
recent reply: (journalist) Why did you find the manager is rude? (customer) The manager didn't greet me when I entered the dealership. He was on the phone and didn't even look at me.
missing detail: How long the customer waited for the manager to finish the phone call and how the manager behaved afterwards is not mentioned.

previous story: The customer went to a hotel and stayed for a night. 
recent reply: (journalist) How did you find the hotel? (customer) It's a nice hotel. The room is clean and the bed is comfortable. But the breakfast is not good.
missing detail: The customer said the breakfast is not good, but the exact reason why it's not good is not mentioned.


OK. Now it's your turn to find a missing detail in the interviewee's response and provide it to the journalist.
previous story: {previous_story}
recent reply: {recent_reply}
missing detail:
"""
    )

    chain = prompt | chat_model_openai_4o.with_structured_output(MissingDetail)

    missing_detail = chain.invoke(
        {
            "previous_story": documents.review.story,
            "recent_reply": messages_to_string(
                documents.review.messages[-2:],
                ai_role="journalist",
                user_role="customer",
            ),
        }
    ).content
    print("    : story_and_reply ->", missing_detail)

    documents.parallel_state.pending_items.append(
        StateItem(
            attribute="missing_details", key="story_and_reply", value=missing_detail
        )
    )

    return {"documents": documents}


def find_missing_detail_story_only(state: dict[str, Documents]):
    print("\n==>> find_missing_detail_story_only")
    documents = state["documents"]

    prompt = PromptTemplate.from_template(
        """
You are helping a journalist at a famous magazine with 40+ years of experience. The reporter's main area of topic is about how customers experienced services, products, and businesses. Her stories are always well-researched and well-written, which a lot of readers appreciate. 
In this specific task, you are going to assist the journalist by finding missing details from the interviewee's response. Once you provide the missing detail, the journalist will ask the interviewee about it.

Here are some examples:

story: The customer went to a restaurant and ordered a steak. The steak was overcooked and the customer was not happy.
missing detail: The customer said it's a high-end restaurant, but the exact price range of the restaurant is not mentioned.

previoud story: The customer went to a car dealership and bought a car. The customer was happy with the car, but the customer service was not good.
missing detail: How long the customer waited for the manager to finish the phone call and how the manager behaved afterwards is not mentioned.

story: The customer went to a hotel and stayed for a night. 
missing detail: The customer said the breakfast is not good, but the exact reason why it's not good is not mentioned.


OK. Now it's your turn to find a missing detail in the story and provide it to the journalist.
story: {story}

DO NOT provide a missing detail that the customer already mentioned that the customer has already stated that they don't know, can't remember, or don't wish to discuss it.
"""
    )

    chain = prompt | chat_model_openai_4o.with_structured_output(MissingDetail)

    missing_detail = chain.invoke(
        {
            "story": documents.review.story,
        }
    ).content
    print("    : story_only ->", missing_detail)

    documents.parallel_state.pending_items.append(
        StateItem(
            attribute="missing_details",
            key="story_only",
            value=missing_detail,
        )
    )

    return {"documents": documents}
