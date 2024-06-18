from varname import nameof as n
from typing import Literal

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field

from app.langchain.schema import Documents
from app.schemas.schemas import State, Role, Message, StateItem


# add context to the state
def gather_user_info(state: dict[str, Documents]):
    print("\n==>> gather_user_info")
    documents = state["documents"]

    user_info = ""
    for bio in documents.user.bios:
        user_info += f"{bio.title}: {bio.content}\n"

    documents.parallel_state.pending_items.append(
        StateItem(attribute="context", key=n(user_info), value=user_info)
    )
    print("    : added user info to context")

    return {"documents": documents}


def gather_vendor_info(state: dict[str, Documents]):
    print("\n==>> gather_vendor_info")
    documents = state["documents"]

    vendor = documents.vendor

    vendor_info = f"Name: {vendor.name}\nAddress: {vendor.address}"

    documents.parallel_state.pending_items.append(
        StateItem(attribute="context", key=n(vendor_info), value=vendor_info)
    )
    print("    : added vendor info to context")

    return {"documents": documents}
