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
    end_conversation,
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
graph.add_conditional_edges(
    "start",
    what_stage_of_chat,
    {
        "start_of_chat": "start_of_chat",
        "middle_of_chat": "middle_of_chat",
        "end_of_chat": "end_of_chat",
    },
)

graph.add_node("start_of_chat", passthrough_node)
graph.add_conditional_edges(
    "start_of_chat",
    is_user_name,
    {
        "ask_name": "ask_name",
        "greeting": "greeting",
    },
)

graph.add_node("middle_of_chat", passthrough_node)
graph.add_conditional_edges(
    "middle_of_chat",
    middle_router,
    {
        "find_relevant_report": "find_relevant_report",
        "find_to_update": "find_to_update",
    },
    then="generate_reply",
)


graph.add_node("end_of_chat", passthrough_node)
graph.add_edge("end_of_chat", "end_conversation")

graph.add_node("end_conversation", end_conversation)
graph.add_edge("end_conversation", "sync_state_doc")

graph.add_node("ask_name", ask_name)
graph.add_edge("ask_name", "sync_state_doc")

graph.add_node("greeting", greeting)
graph.add_edge("greeting", "sync_state_doc")

graph.add_node("find_relevant_report", find_relevant_report)
graph.add_edge("find_relevant_report", "generate_reply")

graph.add_node("find_to_update", find_to_update)
graph.add_edge("find_to_update", "generate_reply")

graph.add_node("generate_reply", generate_reply)
graph.add_edge("generate_reply", "sync_state_doc")

graph.add_node("sync_state_doc", sync_state_doc)
graph.add_edge("sync_state_doc", END)

graph.set_entry_point("start")
langgraph_app = graph.compile()

# visualize the graph

# img = langgraph_app.get_graph().draw_png()
# print(img)
