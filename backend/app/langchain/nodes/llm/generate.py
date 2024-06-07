from bson import ObjectId
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from app.langchain.schema import Documents
from app.langchain.utils.converters import to_role_content_tuples
from app.langchain.common import llm, chat_model, output_parser, chat_model_openai_4o

from langchain_core.pydantic_v1 import BaseModel, Field

from app.langchain.utils.converters import messages_to_string, bios_to_string


class UpdateStory(BaseModel):
    """A story that is being updated with a reply from a customer."""

    content: str = Field(description="The content of the story.")
    title: str = Field(description="The title of the story in 7 words or less.")


def update_story(state: dict[str, Documents]):
    print("\n==>> update_story")
    documents = state["documents"]

    prompt = PromptTemplate.from_template(
        """
You are a journalist at a famous magazine with 40+ years of experience. Your main area of topic is about how customers experienced services, products, and businesses. Your stories are always well-researched and well-written, which a lot of readers appreciate. 
In this particular task, you'll be refining a story based on the customer's interview responses. You'll receive the customer's replies one by one, along with the preceding story. Your task is to seamlessly weave the reply into the narrative in a way that enhances the overall story. Write the story from the first-person perspective, as if you are the customer. Moreover, the narrative should be engaging and descriptive to captivate readers, much like a compelling review.

---
Here are some examples:

previous story: I went to a restaurant and ordered a steak. The steak was overcooked and I was not happy.
recent reply: journalist asked <Did you ask the waiter to cook it less?> customer replied <Yes, I did. I emphasized that I wanted it medium-rare. Can't believe that this happened to this kind of high-end restaurant.>
updated story: I recently visited a high-end restaurant, and ordered a steak. Unfortunately, the steak was overcooked, which left me quite unhappy. I asked the waiter to have it cooked less and emphasized that I wanted it medium-rare. I can't believe this happened at such a high-end restaurant. It was really disappointing given the reputation and expectations I had.

previoud story: I went to a car dealership and bought a car. I was happy with the car, but customer service was not good.
recent reply: journalist asked <Why did you find the manager is rude?> customer replied <The manager didn't greet me when I entered the dealership. He was on the phone and didn't even look at me.>
updated story: I recently went to a car dealership to buy a car. While I'm happy with the car I purchased, the customer service was disappointing. When I entered the dealership, the manager didn't greet me. They were on the phone and didn't even look at me. It made the experience feel unwelcoming despite being satisfied with the car itself.

previous story: I went to a hotel and stayed for a night. 
recent reply: journalist asked <How did you find the hotel?> customer replied <It's a nice hotel. The room is clean and the bed is comfortable. But the breakfast is not good.>
updated story: I stayed at a hotel for a night and overall, it was a decent experience. The hotel itself is nice, the room was clean, and the bed was really comfortable. However, the breakfast was disappointing. The quality just didn't match the rest of the stay. It’s a shame because everything else was great.

previous story: I got my hair done from a guy at a salon. I asked for curtain bangs, but he cut them so short that it’s impossible to style them. When I complained, the salon said this is standard and insisted that I look completely fine. They did not offer any compensation or solution for the bad haircut. It felt so bad. How could a hairstylist insist a customer to feel a certain way! I'm so annoyed.
recent reply: journalist asked <I totally get that, it's really upsetting when someone dismisses your feelings like that 😤. Did you end up finding another solution or another place to fix it?> customer replied <No. I have to just wait until my hair grows back and find another salon.>
updated story: I recently had an awful experience at a Salon. I went in excited to get curtain bangs, but the stylist cut them so short that they're impossible to style. I was really disappointed and frustrated. When I told them I wasn't happy with the cut, they just brushed it off, saying this was standard and that I looked fine. They didn't offer any compensation or solution. It felt so dismissive, like my feelings didn't matter at all. Now I'm stuck waiting for my hair to grow back, and I’ll definitely be looking for a new salon in the future. Would not recommend this place at all!

---
OK, now it's your turn!

previous story: {previous_story}
recent reply: {recent_reply}
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
    )
    print("    : updated_story ->", updated_story.content)

    if getattr(documents.state, "stories", None) is None:
        documents.state.stories = []

    documents.review.story = updated_story.content
    documents.review.title = updated_story.title

    return {"documents": documents}


class Reply(BaseModel):
    """A reply from a journalist to a customer."""

    reaction: str = Field(description="The reaction part of the reply")
    question: str = Field(description="The question part of the reply")


def generate_reply(state: dict[str, Documents]):
    print("\n==>> generate_reply")
    documents = state["documents"]

    messages = to_role_content_tuples(documents.review.messages[-8:])
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
With over 40 years of experience as a journalist for a renowned magazine, you specialize in reporting on customer experiences with services, products, and businesses. Your well-researched and eloquently written stories are greatly appreciated by many readers.
In this task, your role involves texting a customer you're currently interviewing. With your assistant having unearthed some gaps in information, you'll need to fill in these missing details by asking the customer about them.
Remember, your approach to interacting with the customer can greatly influence the depth of information they share. Validating the customer's feelings can encourage them to reveal more, while excessive verbosity may divert them from their emotions.
Appropriate use of emojis can add a touch of warmth to your conversation, making it more engaging. Likewise, conversational language can make the customer feel at ease and more likely to share openly.
As an experienced journalist, you instinctively know the best way to connect with interviewees.

---
Customer information: {customer_info}
The missing detail you need to ask: {missing_detail}

DO NOT FORGET THAT YOU CAN USE EMOJIES IF NEEDED!!
DO USE A COLLOQUIAL LANGUAGE TO MAKE THE CUSTOMER MORE COMFORTABLE!!
DO NOT USE THE SAME REACTION OR QUESTION TWICE!!
DO NOT FORGET THAT YOU CAN USE EMOJIES IF NEEDED!!
DO USE A COLLOQUIAL LANGUAGE TO MAKE THE CUSTOMER MORE COMFORTABLE!!
DO NOT USE THE SAME REACTION OR QUESTION TWICE!!
""",
            ),
            *messages,
        ]
    )

    chain = prompt | chat_model_openai_4o.with_structured_output(Reply)

    candidate_reply_message = chain.invoke(
        {
            "missing_detail": documents.state.chosen_missing_detail,
            "customer_info": bios_to_string(documents.user.bios),
        }
    )

    print("    : reaction ->", candidate_reply_message.reaction)
    print("    : question ->", candidate_reply_message.question)
    documents.state.candidate_reply_message = candidate_reply_message

    return {"documents": documents}
