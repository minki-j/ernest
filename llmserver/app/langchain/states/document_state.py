from typing import TypedDict, Annotated

class DocumentState(TypedDict):
    phone_number: str
    created_at: str
    updated_at: str
    user_info: object
    messages: list
    topics: list[dict[list[dict]]] # a list of topics(dict) that contain a list of questions(dict)
    ephemeral: dict # to pass data between nodes
