from varname import nameof as n

from langgraph.graph import END, StateGraph
from langchain_core.runnables import RunnablePassthrough

from app.langchain.schema import StateType

from app.langchain.utils.converters import to_path_map

from app.langchain.subgraphs.start_of_chat.graph import start_of_chat
from app.langchain.subgraphs.middle_of_chat.graph import middle_of_chat
from app.langchain.subgraphs.end_of_chat.graph import end_of_chat
from app.langchain.subgraphs.ask_vendor_info.graph import ask_vendor_info

from app.langchain.conditional_edges.non_llm.simple_check import what_stage_of_chat
from app.langchain.nodes.non_llm.state_control import sync_state_and_doc

g = StateGraph(StateType)
g.add_node("entry", RunnablePassthrough())
g.set_entry_point("entry")

g.add_conditional_edges(
    "entry",
    what_stage_of_chat,
    to_path_map(
        [
            n(start_of_chat),
            n(ask_vendor_info),
            n(middle_of_chat),
            n(end_of_chat),
        ]
    ),
    then=n(sync_state_and_doc),
)

g.add_node(n(start_of_chat), start_of_chat)
g.add_node(n(ask_vendor_info), ask_vendor_info)
g.add_node(n(middle_of_chat), middle_of_chat)
g.add_node(n(end_of_chat), end_of_chat)

g.add_node(n(sync_state_and_doc), sync_state_and_doc)
g.add_edge(n(sync_state_and_doc), END)

langgraph_app = g.compile()


# with open("graph_imgs/main_graph.png", "wb") as f:
#     f.write(langgraph_app.get_graph().draw_mermaid_png())
