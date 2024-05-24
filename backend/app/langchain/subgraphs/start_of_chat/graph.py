from varname import nameof as n

from langgraph.graph import END, StateGraph
from langchain_core.runnables import RunnablePassthrough

from app.langchain.schema import StateType
from app.schemas.schemas import State, User, Review, Report
from app.langchain.utils.converters import to_path_map

from app.langchain.conditional_edges.non_llm.simple_check import is_user_name
from app.langchain.nodes.non_llm.predefined_reply import ask_name, greeting


g = StateGraph(StateType)
g.set_entry_point("entry")

g.add_node("entry", RunnablePassthrough())
g.add_conditional_edges(
    "entry",
    is_user_name,
    to_path_map(
        [
            n(ask_name),
            n(greeting),
        ]
    ),
    then=END,
)

g.add_node(n(ask_name), ask_name)
g.add_node(n(greeting), greeting)

start_of_chat = g.compile()
