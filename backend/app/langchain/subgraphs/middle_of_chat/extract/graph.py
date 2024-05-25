from typing import Annotated, TypedDict
from varname import nameof as n
from langgraph.graph import END, StateGraph
from langchain_core.runnables import RunnablePassthrough

from app.langchain.schema import StateType
from app.langchain.schema import Documents
from app.schemas.schemas import State, User, Review, Report
from app.langchain.utils.converters import to_path_map

from app.langchain.nodes.llm.extract import (
    extract_user_info_from_reply,
    extract_vendor_info_from_reply,
)


g = StateGraph(StateType)
g.set_entry_point("entry")

g.add_node("entry", RunnablePassthrough())
g.add_edge("entry", n(extract_user_info_from_reply))
g.add_edge("entry", n(extract_vendor_info_from_reply))

g.add_node(n(extract_user_info_from_reply), extract_user_info_from_reply)
g.add_node(n(extract_vendor_info_from_reply), extract_vendor_info_from_reply)

g.add_edge(n(extract_user_info_from_reply), "rendezvous")
g.add_edge(n(extract_vendor_info_from_reply), "rendezvous")

g.add_node("rendezvous", RunnablePassthrough())
g.add_edge("rendezvous", END)

extract = g.compile()
