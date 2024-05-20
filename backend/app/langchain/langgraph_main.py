from langgraph.graph import END, StateGraph
from langchain_core.runnables import RunnablePassthrough

from app.langchain.common import Documents
from app.schemas.schemas import State

from app.langchain.conditional_edges.pick_by_llm import is_reply_A_to_Q, middle_router
from app.langchain.conditional_edges.simple_check import (
    what_stage_of_chat,
    is_user_name,
)

from app.common import vol

# from app.langchain.nodes.decide import (

# )
from app.langchain.nodes.generate import (
    greeting,
    generate_reply,
    ask_name,
    end_of_chat,
)

from app.langchain.nodes.check import find_relevant_report, find_to_update

from app.langchain.nodes.update import update_user_name, dead_end

from app.langchain.nodes.state_control import sync_state_doc

passthrough_node = RunnablePassthrough()

# Features to add
# todo: export the report of the review
# todo: Add quantitaive version of question
# todo: conceal PII when asked
# todo: discard previous answer when asked
# todo: add local llama3 model

graph = StateGraph({"documents": Documents()})

graph.add_node("start", passthrough_node)
graph.set_entry_point("start")

# ------------  Head  ------------
graph.add_conditional_edges(
    "start",
    what_stage_of_chat,
    {
        "start_of_chat": "start_of_chat",
        "middle_of_chat": "middle_of_chat",
        "end_of_chat": "end_of_chat",
    },
    then="sync_state_doc",
)

# ------------  Start of chat (SOC)  ------------
soc_builder = StateGraph({"documents": Documents()})
soc_builder.add_node("start", passthrough_node)
soc_builder.set_entry_point("start")
soc_builder.add_conditional_edges(
    "start",
    is_user_name,
    {
        "ask_name": "ask_name",
        "greeting": "greeting",
    },
    then=END,
)

soc_builder.add_node("ask_name", ask_name)
soc_builder.add_node("greeting", greeting)

graph.add_node("start_of_chat", soc_builder.compile())

# ------------  Middle of chat (MOC)  ------------
moc_builder = StateGraph({"documents": Documents()})
moc_builder.add_node("start", passthrough_node)
moc_builder.set_entry_point("start")
moc_builder.add_conditional_edges(
    "start",
    middle_router,
    {
        "find_relevant_report": "find_relevant_report",
        "find_to_update": "find_to_update",
    },
    then="generate_reply",
)

moc_builder.add_node("find_relevant_report", find_relevant_report)
moc_builder.add_edge("find_relevant_report", "generate_reply")

moc_builder.add_node("find_to_update", find_to_update)
moc_builder.add_edge("find_to_update", "generate_reply")

moc_builder.add_node("generate_reply", generate_reply)
moc_builder.add_edge("generate_reply", END)

graph.add_node("middle_of_chat", moc_builder.compile())

# ------------  End of chat (EOC) ------------
eoc_builder = StateGraph({"documents": Documents()})
eoc_builder.add_node("end_of_chat", end_of_chat)
eoc_builder.set_entry_point("end_of_chat")
eoc_builder.add_edge("end_of_chat", END)

graph.add_node("end_of_chat", eoc_builder.compile())

# ------------  Tail  ------------
graph.add_node("sync_state_doc", sync_state_doc)
graph.add_edge("sync_state_doc", END)

langgraph_app = graph.compile()

# visualize the graph

# img = langgraph_app.get_graph().draw_ascii()
# print(img)
