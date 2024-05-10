from typing import TypedDict, Annotated

class DocumentState(TypedDict):
    phone_number: str
    name: str
    created_at: str
    updated_at: str
    user_info: object
    messages: list
    questions: list
    ephemeral: dict
