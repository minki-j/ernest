from bson import ObjectId
from datetime import datetime
from enum import Enum

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from app.langchain.schema import Documents
from app.langchain.utils.converters import to_role_content_tuples
from app.langchain.common import llm, chat_model, output_parser, chat_model_openai_4o

from langchain_core.pydantic_v1 import BaseModel, Field

from app.langchain.utils.converters import messages_to_string


class MissingDetail(Enum):
    """A missing detail that the journalist should ask"""

    story_and_reply = "story_and_reply"
    story_only = "story_only"

class BestMissingDetail(BaseModel):
    """The best missing detail that the journalist should ask"""

    reason: str = Field(description="The reason why the detail is the best choice.")
    choice: MissingDetail 


def pick_best_missing_detail(state: dict[str, Documents]):
    print("\n==>> pick_best_missing_detail")
    documents = state["documents"]

    prompt = PromptTemplate.from_template(
        """
You are helping a journalist at a famous magazine with 40+ years of experience. The reporter's main area of topic is about how customers experienced services, products, and businesses. Her stories are always well-researched and well-written, which a lot of readers appreciate.
Your task is to pick the best missing detail that the journalist should ask the interviewee. You will be provided with the story and the conversation between the journalist and the interviewee. You need to decide whether the best missing detail is from provided options.
Remember that the journalist will ask the interviewee about the missing detail you picked. Consider from the interviewee's perspective and make sure the chosen missing detail is not repetitive or irrelevant. Make sure that the chosen missing detail is natural to ask in the context of the latest conversation.

Lastest conversation: {conversation}
Summarized story: {story}

Missing Detail options from which you need to pick the best one:
story_and_reply: {story_and_reply}
story_only: {story_only}
        """
    )

    chain = prompt | chat_model.with_structured_output(BestMissingDetail)

    best_missing_detail = chain.invoke(
        {
            "story": documents.review.story,
            "conversation": messages_to_string(documents.review.messages[-10:]),
            "story_and_reply": documents.state.missing_details["story_and_reply"],
            "story_only": documents.state.missing_details["story_only"],
        }
    )
    print("     best missing detail:", best_missing_detail.choice.value)
    print("     reason:", best_missing_detail.reason)

    if best_missing_detail.choice == MissingDetail.story_and_reply:
        documents.state.chosen_missing_detail = documents.state.missing_details[
            "story_and_reply"
        ]
    elif best_missing_detail.choice == MissingDetail.story_only:
        documents.state.chosen_missing_detail = documents.state.missing_details[
            "story_only"
        ]
    else:
        raise ValueError("Invalid best missing detail choice")

    return {"documents": documents}
