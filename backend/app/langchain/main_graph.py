from varname import nameof as n

from langgraph.graph import END, StateGraph
from langchain_core.runnables import RunnablePassthrough

from app.langchain.schema import StateType
from app.langchain.conditional_edges.non_llm.simple_check import what_stage_of_chat
from app.langchain.nodes.non_llm.state_control import sync_state_and_doc
from app.langchain.utils.converters import to_path_map

from app.langchain.subgraphs.start_of_chat.graph import start_of_chat
from app.langchain.subgraphs.middle_of_chat.graph import middle_of_chat
from app.langchain.subgraphs.end_of_chat.graph import end_of_chat

# Features to add
# todo: export the report of the review
# todo: Add quantitaive version of question
# todo: conceal PII when asked
# todo: discard previous answer when asked
# todo: add local llama3 model


g = StateGraph(StateType)
g.set_entry_point("entry")

g.add_node("entry", RunnablePassthrough())

g.add_conditional_edges(
    "entry",
    what_stage_of_chat,
    to_path_map(
        [
            n(start_of_chat),
            n(middle_of_chat),
            n(end_of_chat),
        ]
    ),
    then=n(sync_state_and_doc),
)

g.add_node(n(start_of_chat), start_of_chat)
g.add_node(n(middle_of_chat), middle_of_chat)
g.add_node(n(end_of_chat), end_of_chat)

g.add_node(n(sync_state_and_doc), sync_state_and_doc)
g.add_edge(n(sync_state_and_doc), END)

langgraph_app = g.compile()


# with open("main_graph.png", "wb") as f:
#     f.write(langgraph_app.get_graph().draw_png())
