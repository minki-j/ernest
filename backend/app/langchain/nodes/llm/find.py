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

    missing_detail_1: str = Field(description="The content of the detail.")
    missing_detail_2: str = Field(description="The content of the detail.")
    missing_detail_3: str = Field(description="The content of the detail.")


def find_missing_detail_with_reply(state: dict[str, Documents]):
    print("\n==>> find_missing_detail_with_reply")
    documents = state["documents"]

    prompt = PromptTemplate.from_template(
        """
You are helping a journalist at a famous magazine with 40+ years of experience. The reporter's main area of topic is about how customers experienced services, products, and businesses. Her stories are always well-researched and well-written, which a lot of readers appreciate. 
In this specific task, you are going to assist the journalist by finding missing details from the interviewee's response. Once you provide the missing detail, the journalist will ask the interviewee about it. You can return None if you can't find any missing detail.

Here are some examples:

previous story: I went to a restaurant and ordered a steak. The steak was overcooked and I was not happy.
recent reply: (journalist) Did you ask the waiter to cook it less? (customer) Yes, I did. I emphasized that I wanted it medium-rare. Can't believe that this happened to this kind of high-end restaurant.
missing detail 1: The customer said it's a high-end restaurant, but the exact price range of the restaurant is not mentioned.
missing detail 2: Whether the customer complained to the waiter about the overcooked steak.
missing detail 3: If there were any other complaints about the restaurant.


previoud story: I went to a car dealership and bought a car. I was happy with the car, but I service was not good.
recent reply: (journalist) Why did you find the manager is rude? (customer) The manager didn't greet me when I entered the dealership. He was on the phone and didn't even look at me.
missing detail 1: How long the customer waited for the manager to finish the phone call.
missing detail 2: If the customer complained to the manager about the rude behavior.
missing detail 3: If the manager apologized after the phone call.

previous story: I went to a hotel and stayed for a night. 
recent reply: (journalist) How did you find the hotel? (customer) It's a nice hotel. The room is clean and the bed is comfortable. But the breakfast is not good.
missing detail 1: The customer said the breakfast is not good, but the exact reason why it's not good is not mentioned.
missing detail 2: What range of price the customer paid for the hotel.
missing detail 3: None

previous story: I recently got a haircut, and it turned out horribly. I was really looking forward to a fresh new look, but it was a complete letdown. The stylist just didn't get it right at all, and now I'm stuck with a haircut I absolutely hate. I had specifically asked for a toner for my faded highlights, requesting a light ash toner. Instead, I received a dark blonde toner that looks purple in the daylight. It's incredibly frustrating to have such a glaring mistake, especially after clearly communicating what I wanted. Unfortunately, I didn't realize how bad it was until after I left the salon. By the time I noticed, I was already home, and it was too late to go back and have it fixed. I would just think I wasted 300 dollars. I don't think they are willing to and capable of fixing my hair. When asked if I sought a refund or compensation for the botched haircut, I realized I hadn't even tried. I don't want to be engaged with them any further. The whole experience was so disheartening that I'd rather cut my losses and move on.
recent reply: journalist asked <Ugh, I'm so sorry to hear that! $300 is a lot to spend for something that didn't turn out right 😤 Did you try to seek a refund or any compensation for the botched haircut?>, customer replied <No. I havent' tried. I don't want to be engaged with them.>
missing detail 1: What's the name of the salon?
missing detail 2: Was the price reasonable for the service compared to other salons?
missing detail 3: Have you ever done your hair at this salon before?

OK. Now it's your turn to find a missing detail in the interviewee's response and provide it to the journalist.
previous story: {previous_story}
recent reply: {recent_reply}
"""
    )

    chain = prompt | chat_model_openai_4o.with_structured_output(MissingDetail)

    missing_details = chain.invoke(
        {
            "previous_story": documents.review.story,
            "recent_reply": messages_to_string(
                documents.review.messages[-2:],
                ai_role="journalist",
                user_role="customer",
            ),
        }
    )
    missing_details = list(missing_details.dict().values())
    print("    : story_and_reply ->", missing_details)

    documents.parallel_state.pending_items.append(
        StateItem(
            attribute="missing_details", key="story_and_reply", value=missing_details
        )
    )

    return {"documents": documents}


def find_missing_detail_story_only(state: dict[str, Documents]):
    print("\n==>> find_missing_detail_story_only")
    documents = state["documents"]

    prompt = PromptTemplate.from_template(
        """
You are helping a journalist at a famous magazine with 40+ years of experience. The reporter's main area of topic is about how customers experienced services, products, and businesses. Her stories are always well-researched and well-written, which a lot of readers appreciate. 
In this specific task, you are going to assist the journalist by finding missing details from the interviewee's response with which the journalist can ask the interviewee about it.

Here are some examples:

story: I went to a restaurant and ordered a steak. The steak was overcooked and I was not happy.
missing detail 1: The customer said the steak was overcooked, but if they asked the waiter to cook it less is not mentioned.
missing detail 2: Whether the customer complained to the waiter about the overcooked steak.
missing detail 3: If there were any other complaints about the restaurant.

previoud story: I went to a car dealershop and bought a car. I was happy with the car, but the service was not good. The dealer was rude and didn't greet me when I entered the dealership. When I asked about the car, he was very impatient and didn't answer my questions properly.
missing detail 1: What's the name of dealer?
missing detail 2: Was it a new or used car?
missing detail 3: If the customer complained to the manager about the rude behavior.

story: I went to a hotel and stayed for a night. 
missing detail 1: The customer said they stayed at a hotel but didn't mention how their experience was with the hotel.
missing detail 2: What range of price the customer paid for the hotel.
missing detail 3: If there were someone else staying at the hotel with the customer.


OK. Now it's your turn to find a missing detail in the story and provide it to the journalist.
story: {story}

DO NOT provide a missing detail that the customer has already stated that they don't know, can't remember, or don't wish to discuss about it.
"""
    )

    chain = prompt | chat_model_openai_4o.with_structured_output(MissingDetail)

    missing_details = chain.invoke(
        {
            "story": documents.review.story,
        }
    )
    missing_details = list(missing_details.dict().values())
    print("    : story_only ->", missing_details)

    documents.parallel_state.pending_items.append(
        StateItem(
            attribute="missing_details",
            key="story_only",
            value=missing_details,
        )
    )

    return {"documents": documents}


class Questions(BaseModel):
    """Questions to ask the customer"""

    question_1: str = Field(description="The content of the question.")
    question_2: str = Field(description="The content of the question.")
    question_3: str = Field(description="The content of the question.")

def find_missing_detail_from_customer_perspective(state: dict[str, Documents]):
    print("\n==>> find_missing_detail_from_customer_perspective")
    documents = state["documents"]

    prompt = PromptTemplate.from_template(
        """
Imagine you are the customer in the story and conversation. You are being interviewed by a journalist at a famous magazine with 40+ years of experience. The reporter's main area of topic is about how customers experienced services, products, and businesses. Her stories are always well-researched and well-written, which a lot of readers appreciate.
What question would you like the journalist to ask you about the story and conversation? Again, IMAGINE that you are the customer in the story and conversation.
story: {story}
conversation: {conversation}
"""
    )

    chain = prompt | chat_model_openai_4o.with_structured_output(Questions)

    questions = chain.invoke(
        {
            "story": documents.review.story,
            "conversation": messages_to_string(documents.review.messages[-20:]),
        }
    )
    questions = list(questions.dict().values())
    print("    : customer_perspective ->", questions)

    documents.parallel_state.pending_items.append(
        StateItem(
            attribute="missing_details",
            key="customer_perspective",
            value=questions,
        )
    )

    return {"documents": documents}
