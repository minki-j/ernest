from varname import nameof as n

from langgraph.graph import END, StateGraph
from langchain_core.runnables import RunnablePassthrough

from app.langchain.schema import StateType
from app.schemas.schemas import State, User, Review, Report
from app.langchain.utils.converters import to_path_map

from app.langchain.nodes.non_llm.predefined_reply import ask_user_name
from app.langchain.nodes.llm.extract import extract_necessary_info
from app.langchain.nodes.non_llm.predefined_reply import ask_vendor_info
from app.langchain.conditional_edges.llm.check import check_necessary_inquiries
from app.langchain.nodes.non_llm.predefined_reply import introduction

g = StateGraph(StateType)
g.set_entry_point("entry")

g.add_node("entry", RunnablePassthrough())
g.add_edge("entry", n(extract_necessary_info))

g.add_node(n(extract_necessary_info), extract_necessary_info)
g.add_conditional_edges(
    n(extract_necessary_info),
    check_necessary_inquiries,
    to_path_map(
        [
            n(ask_vendor_info),
            n(ask_user_name),
            n(introduction),
        ]
    ),
    then=END
)

g.add_node(n(ask_vendor_info), ask_vendor_info)
g.add_node(n(ask_user_name), ask_user_name)
g.add_node(n(introduction), introduction)


start_of_chat = g.compile()
