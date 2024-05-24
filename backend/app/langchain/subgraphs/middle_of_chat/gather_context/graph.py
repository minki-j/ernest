from typing import Annotated, TypedDict
from varname import nameof as n
from langgraph.graph import END, StateGraph
from langchain_core.runnables import RunnablePassthrough

from app.langchain.schema import StateType
from app.langchain.schema import Documents
from app.schemas.schemas import State, User, Review, Report
from app.langchain.utils.converters import to_path_map
from app.langchain.nodes.non_llm.gather_context import (
    gather_user_info,
    gather_vendor_info,
)

g = StateGraph(StateType)
g.set_entry_point("entry")

g.add_node("entry", RunnablePassthrough())

g.add_edge("entry", n(gather_user_info))
g.add_edge("entry", n(gather_vendor_info))

g.add_node(n(gather_user_info), gather_user_info)
g.add_node(n(gather_vendor_info), gather_vendor_info)

g.add_edge(n(gather_user_info), "rendezvous")
g.add_edge(n(gather_vendor_info), "rendezvous")

g.add_node("rendezvous", RunnablePassthrough())
g.add_edge("rendezvous", END)

gather_context = g.compile()
