from typing import TypedDict

from app.schemas.schemas import Review, User, Vendor, State, Message, Payment, QA_pair, State

from langchain_core.output_parsers import StrOutputParser
output_parser = StrOutputParser()

from langchain_openai import ChatOpenAI, OpenAI
chat_model = ChatOpenAI(model="gpt-3.5-turbo")
llm = OpenAI(model="gpt-3.5-turbo")

# from langchain_anthropic import ChatAnthropic, Anthropic
# chat_model = ChatAnthropic(model="claude-3-haiku-20240307")
# llm = Anthropic(model="claude-3-haiku-20240307")

class Documents(TypedDict):
    review: Review
    user: User
    vendor: Vendor
    state: State

    def update(self, value):
        if isinstance(value, State):
            self.review["state"] = value
            return
        elif isinstance(value, Message):
            self.review["conversations"].append(value)
            return
        elif isinstance(value, list) and all(isinstance(item, Message) for item in value):
            self.review["conversations"].extend(value)
            return
        elif isinstance(value, Payment):
            self.review["payment_info"].append(value)
            return
        elif isinstance(value, QA_pair):
            self.review["qa_pairs"].append(value)
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
        elif isinstance(value, State):
            self.state = value
            return
        else:
            raise ValueError(f"Unsupported type {type(value)}")