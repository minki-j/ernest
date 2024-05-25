from typing import Annotated, TypedDict
from app.schemas.schemas import (
    Message,
    Payment,
    Report,
    Review,
    State,
    ParallelState,
    User,
    Vendor,
    StateItem,
    Bio,
)


class Documents():
    review: Review
    user: User
    vendor: Vendor
    state: State
    parallel_state: ParallelState

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        result = {}
        for attr in ["review", "user", "vendor", "state", "parallel_state"]:
            value = getattr(self, attr, None)
            if value is not None and hasattr(value, 'to_dict'):
                result[attr] = value.to_dict()
        return result

    def add(self, value):
        if isinstance(value, State):
            self.state = value
            return
        elif isinstance(value, StateItem):
            if not hasattr(self.state, value.attribute):
                setattr(self.state, value.attribute, {})
            getattr(self.state, value.attribute)[value.key] = value.value
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
        elif isinstance(value, Bio):
            self.user.bios.append(value)
        elif isinstance(value, Vendor):
            self.vendor = value
            return
        else:
            raise ValueError(f"Unsupported type {type(value)}")


class StateType(TypedDict):

    @staticmethod
    def merge_docs(_doc_a: Documents, doc_b: Documents) -> Documents:        
        while doc_b.parallel_state.pending_items:
            item = doc_b.parallel_state.pending_items.pop()
            doc_b.add(item)

        return doc_b

    documents: Annotated[Documents, merge_docs]
