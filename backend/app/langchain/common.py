from typing import TypedDict, Annotated

from app.schemas.schemas import (
    Review,
    User,
    Vendor,
    State,
    Message,
    Payment,
    Report,
)

from langchain_core.output_parsers import StrOutputParser
output_parser = StrOutputParser()

from langchain_openai import ChatOpenAI, OpenAI
chat_model = ChatOpenAI(model="gpt-3.5-turbo")
llm = OpenAI(model="gpt-3.5-turbo")

# from langchain_anthropic import ChatAnthropic, Anthropic
# chat_model = ChatAnthropic(model="claude-3-haiku-20240307")
# llm = Anthropic(model="claude-3-haiku-20240307")


class Documents():
    review: Review 
    user: User 
    vendor: Vendor 
    state: State

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        result = {}
        for attr in ['review', 'user', 'vendor', 'state']:
            value = getattr(self, attr, None)
            if value is not None and hasattr(value, 'to_dict'):
                result[attr] = value.to_dict()
        return result

    def add(self, value):
        if isinstance(value, State):
            self.state = value
            return
        elif isinstance(value, Message):
            self.review.messages.append(value)
            return
        elif isinstance(value, list) and all(isinstance(item, Message) for item in value):
            self.review.messages.extend(value)
            return
        elif isinstance(value, Payment):
            self.review.payment_info.append(value)
            return
        elif isinstance(value, Report):
            self.review.reports.append(value)
            return
        elif isinstance(value, Review):
            self.review = value
            return
        elif isinstance(value, User):
            self.user = value
            return
        elif isinstance(value, Vendor):
            self.vendor = value
            return
        else:
            raise ValueError(f"Unsupported type {type(value)}")


class StateType(TypedDict):
    documents: Annotated[
        Documents, lambda _, new: new
    ]  # replace the new doc with the old doc
