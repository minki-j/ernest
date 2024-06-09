from varname import nameof as n

from langgraph.graph import END, StateGraph
from langchain_core.runnables import RunnablePassthrough

from app.langchain.schema import StateType
from app.schemas.schemas import State, User, Review, Report
from app.langchain.utils.converters import to_path_map

from app.langchain.nodes.non_llm.predefined_reply import ask_vendor_info


g = StateGraph(StateType)
g.set_entry_point("entry")

g.add_node("entry", RunnablePassthrough())
g.add_edge("entry", n(ask_vendor_info))

g.add_node(n(ask_vendor_info), ask_vendor_info)
g.add_edge(n(ask_vendor_info), END)

ask_vendor_info = g.compile()
