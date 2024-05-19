from bson import ObjectId
from enum import Enum
from datetime import datetime
from pydantic import BaseModel

# ! Should I change this to pydantic BaseModel?
# ! Pydantic provides dict() method...
class Base():
    def __init__(self) -> None:
        pass

    def to_dict(self):
        """Recursively convert the object to a dictionary."""
        result_dict = {}
        primitive_types = (int, str, bool, float, bytes, ObjectId)

        for key, value in self.__dict__.items():
            if isinstance(value, primitive_types) or value is None:
                result_dict[key] = value
            elif isinstance(value, list):
                if key not in result_dict:
                    result_dict[key] = []
                for item in value:
                    if isinstance(item, primitive_types):
                        result_dict[key].append(item)
                    elif isinstance(item, Base):
                        result_dict[key].append(item.to_dict())
            elif isinstance(value, dict):
                if key not in result_dict:
                    result_dict[key] = {}
                for k, v in value.items():
                    if isinstance(v, primitive_types):
                        result_dict[key][k] = v
                    elif isinstance(v, Base):
                        result_dict[key][k] = v.to_dict()
            else:
                result_dict[key] = value.to_dict()

        return result_dict


class State(Base):
    reply_message: str

    def __init__(self, **kwargs):
        self.reply_message = "No reply provided"
        for key, value in kwargs.items():
            setattr(self, key, value)


class Role(str, Enum):
    USER = "user"
    AI = "ai"


# There is no id for message. We use order of the message in the conversation to identify it. In order to keep the order, we never delete messages. We just mark them as deleted.
class Message(Base):
    role: Role
    content: str
    created_at: str
    deleted: bool

    def __init__(self, role: Role, content: str, **kwargs):
        self.role = role
        self.content = content
        self.created_at = datetime.now().isoformat()
        self.deleted = False
        for key, value in kwargs.items():
            setattr(self, key, value)


class Report(Base):
    title: str
    content: str
    relevant_msg_orders: list[int]

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class Payment(Base):
    item_name: str
    amount: float
    currency: str
    paid_at: str

    def __init__(self, item_name: str, amount: float, **kwargs):
        self.item_name = item_name
        self.amount = amount
        self.currency = "CAD"
        self.paid_at = datetime.now().isoformat()
        for key, value in kwargs.items():
            setattr(self, key, value)


class Review(Base):
    _id: ObjectId
    user_id: ObjectId
    vendor_id: ObjectId
    payment_info: list[Payment]
    messages: list[Message]
    reports: list[Report]
    created_at: str
    state: State  # we keep the state in the review object

    def __init__(self, user_id:str, **kwargs):
        self.user_id = user_id
        self.vendor_id = None
        self.payment_info = []
        self.messages = []
        self.reports = []
        self.created_at = datetime.now().isoformat()
        self.state = State()
        for key, value in kwargs.items():
            if key == "messages":
                messages = []
                for item in value:
                    messages.append(Message(**item))
                setattr(self, key, messages)
            elif key == "payment_info":
                payments = []
                for item in value:
                    payments.append(Payment(**item))
                setattr(self, key, payments)
            elif key == "reports":
                reports = []
                for item in value:
                    reports.append(Report(**item))
                setattr(self, key, reports)
            elif key == "state":
                setattr(self, key, State(**value))
            else:
                setattr(self, key, value)


class Bio(Base):
    title: str
    content: str
    reference: list[
        (ObjectId, int)
    ]  # first element is the review id, second element is the message order

    def __init__(self, title: str, content: str, **kwargs):
        self.title = title
        self.content = content
        self.reference = []
        for key, value in kwargs.items():
            setattr(self, key, value)


class User(Base):
    _id: ObjectId
    name: str
    email: str
    username: str
    created_at: str
    updated_at: str
    review_ids: list[ObjectId]
    bio: list[Bio]

    def __init__(self, **kwargs):
        self.name = None
        self.email = None
        self.username = None
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.review_ids = []
        self.bio = []
        for key, value in kwargs.items():
            if key == "bio":
                bio = []
                for item in value:
                    bio.append(Bio(**item))
                setattr(self, key, bio)
            else:
                setattr(self, key, value)


class Vendor(Base):
    _id: ObjectId
    name: str
    location: str
    created_at: str
    updated_at: str
    review_ids: list[ObjectId]

    def __init__(self, **kwargs):
        self.name = None
        self.location = None
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.review_ids = []
        for key, value in kwargs.items():
            setattr(self, key, value)
