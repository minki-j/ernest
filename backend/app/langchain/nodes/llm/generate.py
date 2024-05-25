from bson import ObjectId
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from app.langchain.schema import Documents
from app.langchain.utils.converters import to_role_content_tuples
from app.langchain.common import llm, chat_model, output_parser, chat_model_openai_4o

from langchain_core.pydantic_v1 import BaseModel, Field

from app.langchain.utils.converters import messages_to_string

class UpdateStory(BaseModel):
    """A story that is being updated with a reply from a customer."""

    content: str = Field(description="The content of the story.")


def update_story(state: dict[str, Documents]):
    print("==>> update_story")
    documents = state["documents"]

    prompt = PromptTemplate.from_template(
        """
You are a journalist at a famous magazine with 40+ years of experience. Your main area of topic is about how customers experienced services, products, and businesses. Your stories are always well-researched and well-written, which a lot of readers appreciate. 
In this specific task, you are going to incrementally improve the story with what the customer said during the interview. You'll be provided a reply from the customer one by one along with the previous story. You need to incorporate the reply into the story in a way that makes sense and improves the story.


Here are some examples:

previous story: The customer went to a restaurant and ordered a steak. The steak was overcooked and the customer was not happy.
recent reply: (journalist) Did you ask the waiter to cook it less? (customer) Yes, I did. I emphasized that I wanted it medium-rare. Can't believe that this happened to this kind of high-end restaurant.
updated story: The customer went to a high-end restaurant and ordered a steak. The steak was overcooked and the customer was not happy. The customer asked the waiter to cook it less and emphasized that they wanted it medium-rare. The customer can't believe that this happened to this kind of high-end restaurant.

previoud story: The customer went to a car dealership and bought a car. The customer was happy with the car, but the customer service was not good.
recent reply: (journalist) Why did you find the manager is rude? (customer) The manager didn't greet me when I entered the dealership. He was on the phone and didn't even look at me.
updated story: The customer went to a car dealership and bought a car. The customer was happy with the car, but the customer service was not good. The manager didn't greet the customer when they entered the dealership. The manager was on the phone and didn't even look at the customer.

previous story: The customer went to a hotel and stayed for a night. 
recent reply: (journalist) How did you find the hotel? (customer) It's a nice hotel. The room is clean and the bed is comfortable. But the breakfast is not good.
updated story: The customer went to a hotel and stayed for a night. The hotel is nice. The room is clean and the bed is comfortable. But the breakfast is not good.


OK, now it's your turn!

previous story: {previous_story}
recent reply: {recent_reply}
updated story:
"""
    )

    chain = prompt | chat_model_openai_4o.with_structured_output(UpdateStory)

    updated_story = chain.invoke(
        {
            "previous_story": documents.review.story,
            "recent_reply": messages_to_string(
                documents.review.messages[-2:],
                ai_role="journalist",
                user_role="customer",
            ),
        }
    ).content
    print("    : updated_story ->", updated_story)

    if getattr(documents.state, "stories", None) is None:
        documents.state.stories = []

    documents.review.story = updated_story

    return {"documents": documents}


def generate_reply(state: dict[str, Documents]):
    print("==>> generate_reply")
    documents = state["documents"]
    print("    : missing_details ->", documents.state.missing_details[-1])

    messages = to_role_content_tuples(documents.review.messages[-8:])
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
"""
You are a journalist at a famous magazine with 40+ years of experience. Your main area of topic is about how customers experienced services, products, and businesses. Your stories are always well-researched and well-written, which a lot of readers appreciate. 
In this specific task, you are going to reply to the customer that your are interviewing at the moment. Your assistant already did some research and found some missing details. You need to ask the customer about these missing details.
The missing detail is the following: {missing_detail}
Keep in mind that the way you reply to the customer determines how much information you can get from them. For example, validating the customer's feelings can help you get more information from them. On the other hand, being too verbose can distract the customer away from their own feelings. You are a seasoned journalist and you know what is the best way to respond to the interviewee by instinct.
""",
            ),
            *messages,
        ]
    )

    chain = prompt | chat_model_openai_4o | output_parser

    documents.state.reply_message = chain.invoke(
        {
            "missing_detail": documents.state.missing_details[-1],
        }
    )

    return {"documents": documents}
