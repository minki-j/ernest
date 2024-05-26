from typing import Literal

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field

from app.langchain.schema import Documents
from app.schemas.schemas import State, Role, Message

from app.langchain.common import llm, chat_model, output_parser

class Name(BaseModel):
    """Leave None if not found"""

    fist_name: str
    middle_name: str
    last_name: str

    def capitalize(self) -> str:
        if self.fist_name is not None:
            self.fist_name = self.fist_name.capitalize()
        if self.middle_name is not None:
            self.middle_name = self.middle_name.capitalize()
        if self.last_name is not None:
            self.last_name = self.last_name.capitalize()

        return self


def update_user_name(state: dict[str, Documents]):
    print("\n==>> update_user_name")
    documents = state["documents"]

    structured_chat_model = chat_model.with_structured_output(Name)

    user_name = structured_chat_model.invoke(
        documents.review.messages[-1].content
    ).capitalize()

    documents.user.name = (
        (user_name.fist_name + " " if user_name.fist_name else "")
        + (user_name.middle_name + " " if user_name.middle_name else "")
        + (user_name.last_name if user_name.last_name else "")
    )

    return {"documents": documents}
