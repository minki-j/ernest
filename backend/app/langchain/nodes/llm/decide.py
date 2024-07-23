from varname import nameof as n
from enum import Enum
from bson import ObjectId
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from app.langchain.schema import Documents, StateItem, Bio
from app.langchain.utils.converters import messages_to_string

from app.langchain.common import llm, chat_model, output_parser, chat_model_openai_4o

from langchain_core.pydantic_v1 import BaseModel, Field


class Reply(BaseModel):
    """The type of reply the customer has given in the interview."""

    rationale: str = Field(description="The rationale why the chosen type is the best.")
    reply: str = Field(description="The final reply to send to the customer.")


# ! This doesn't work well. It always returns reaction_and_question. Unreliably returns reaction_only.
def decide_reply_type(state: dict[str, Documents]):
    print("\n==>> decide_reply_type")
    documents = state["documents"]

    prompt = PromptTemplate.from_template(
        """
        Here is the recent conversation of a interview about Next JS:
        previous conversation:  journalist asked <Hi I'm Ernest! What's your name?>, customer replied <I'm Minki>, journalist asked <Hi Minki ! Before begin the interview, could you let me know which company or tool you are going to talk about?>, customer replied <I want to talk about Next JS>, journalist asked <Hi Minki ! Thanks for sharing your valuable time and insight on Next JS today. The interview would take roughly 10 mins. Are you ready to begin?>, customer replied <Yes, I'm ready>, journalist asked <Awesome! 😊 Can you tell me a bit about your experience with Next JS? What kind of insights or experiences do you have that qualify you to speak on this topic?>, customer replied <It had quite a bit of learning curve since they devide client and server side. I struggled for a week to get a mental model for that architecture. However, if I set up things correctly it's very efficient thanks to the server side rendering.>

        What would the journalist's response be? Here are some options that you can use:
        possible reaction: "You got the point of thier architecture model of Next JS!"
        possible comment: "Some people mentioned the same problem as you said. They found Next JS learning curve was higher than other frameworks."
        possible question: "What kind of project did you build with Next JS?"

        rationale: "All three options are useful. However, they need to be edited a bit to fit in a single reply. So I'll change the wordings and combine all of the options"
        reply: "That's a great point. You got the gist of their architecture. And yes, the learning curve of Next JS can be high. I've been hearing that from quite many people so far. I'm curious, what kind of project did you build with Next JS?"
        ---
        Here is the recent conversation of a interview about {topic}:
        previous conversation: {conversation}

        What would the journalist's response be? Here are some options that you can use:
        possible reaction: {possible_reaction}
        possible comment: {possible_comment}
        possible question: {possible_question}
        ---
        ---
        Keep in mind that you don't have to use all the options. 
        Make sure that your reply sounds natural when you are mixing different options.
        Don't be verbose and make sure the interviewer can read your reply quickly. 
        """
    )

    chain = prompt | chat_model_openai_4o.with_structured_output(Reply)

    reulst = chain.invoke(
        {
            "topic": documents.vendor.name,
            "conversation": messages_to_string(
                documents.review.messages[-10:],
                ai_role="journalist",
                user_role="customer",
            ),
            "possible_reaction": documents.state.candidate_reply_message["reaction"],
            "possible_question": documents.state.candidate_reply_message["question"],
            "possible_comment": (
                documents.state.candidate_reply_message["referring_to_knowledge_graph"]
                if documents.state.candidate_reply_message.get(
                    "referring_to_knowledge_graph", None
                )
                else "none"
            ),
        }
    )
    print("    rationale:", reulst.rationale)
    print("    reply:", reulst.reply)

    documents.state.reply_message = reulst.reply

    return {"documents": documents}
