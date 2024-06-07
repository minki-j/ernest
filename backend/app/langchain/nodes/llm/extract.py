from varname import nameof as n
from bson import ObjectId
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from app.langchain.schema import Documents, StateItem, Bio
from app.langchain.utils.converters import messages_to_string

from app.langchain.common import llm, chat_model, output_parser, chat_model_openai_4o

from langchain_core.pydantic_v1 import BaseModel, Field

class Item(BaseModel):
    """Extracted information from the conversation."""
    title: str = Field(
        description="A succint title/topic of the extracted information."
    )
    content: str = Field(
        description="A detailed content of the extracted information. Only include what's in the given text"
    )

class Extracted(BaseModel):
    think_out_loud: str = Field(description="Think out loud which information you are going to extract with a valid reasoning.")
    items: list[Item] = Field(description="A list of extracted items.")

def extract_user_info_from_reply(state: dict[str, Documents]):
    print("\n==>> extract_user_info_from_reply")
    documents = state["documents"]

    prompt = PromptTemplate.from_template(
        """
You are a professional counsellor listening to a user's {sentiment} experience from a {vendor_type}. You always keep a separate for each client to remember important information for the future conversation. In the note, you only add the information you think is important to rememeber, not the nitty-gritty details. For example, you may want to remember the user's preferences, opinions, and so on. But not the details or one-time events such as the fact that the user went to school or work yesterday. You can also think out loud to explain why you think the information is important to remember.

Here are some examples:

conversation: (counsellor) What did you do yesterday? (customer) I went to a restaurant yesterday and had a pasta. Pasta is my favorite food.
think out loud: "OK there are two informations in the message. The user went to a restaurant yesterday and had a pasta. The user also mentioned that pasta is their favorite food. The fact that the user went to a restaurant yesterday is not important for the future conversation since it's just one-time event. But the fact that pasta is their favorite food is important to remember for the future conversation because it is a user's preference that doesn't change often."
[{title: "User's favorite food", content: "Pasta"}]

conversation: (counsellor) Why are you upset? What happened? (customer) I wanted to have my dog get a regular checkup by a vet. I went to "Buddy Clinic" and the vet was very friendly.
think out loud: "OK there are two informations in the message. The user wanted to have their dog get a regular checkup by a vet. The user went to "Buddy Clinic" and the vet was very friendly. The fact that the user wanted to have their dog get a regular checkup by a vet is not important for the future conversation since it's just a contextual information for this specific scenario. But the fact that the user went to "Buddy Clinic" and the vet was very friendly is important to remember for the future conversation because it is a user's opinion about the vet."
[{title: "User's experince at "Buddy Clinic", content: "The vet was very friendly"}]

OK. Now it's your turn:
conversation: {conversation}"""
    )

    structured_chat_model = chat_model_openai_4o.with_structured_output(Extracted)
    chain = prompt | structured_chat_model
    extracted = chain.invoke(
        {
            "sentiment": "negative",
            "vendor_type": "hair salon",
            "conversation": messages_to_string(
                documents.review.messages[-2:],
                ai_role="counseller",
                user_role="customer",
            ),
        }
    )
    print(f"    title: {extracted.title}")
    print(f"    content: {extracted.content}")

    documents.parallel_state.pending_items.append(
        # StateItem(attribute="context", key=n(extracted.title), value=extracted.content)
        Bio(title=extracted.title, content=extracted.content)
    )


def extract_vendor_info_from_reply(state: dict[str, Documents]):
    print("\n==>> extract_info_from_vendor_reply")
    documents = state["documents"]
