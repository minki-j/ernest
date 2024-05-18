from langgraph.graph import END, StateGraph
from langchain_core.runnables import RunnablePassthrough

from app.langchain.common import Documents
from app.schemas.schemas import State

from app.langchain.conditional_edges.pick_by_llm import is_reply_A_to_Q
from app.langchain.conditional_edges.simple_check import is_start_of_conversation

# from app.langchain.nodes.decide import (

# )
from app.langchain.nodes.generate import generate_reply

# from app.langchain.nodes.check import (

# )

passthrough_node = RunnablePassthrough()

# Features to add
# todo: export the report of the review
# todo: Add quantitaive version of question
# todo: conceal PII when asked
# todo: discard previous answer when asked
# todo: add local llama3 model

graph = StateGraph({"documents": Documents()})

graph.add_node("start", passthrough_node)
graph.add_conditional_edges("start", is_start_of_conversation)

graph.add_node("decide_next_step", passthrough_node)
graph.add_edge("decide_next_step", "generate_reply")

graph.add_node("generate_reply", generate_reply)
graph.add_edge("generate_reply", END)

graph.set_entry_point("start")
langgraph_app = graph.compile()

# visualize the graph
# langgraph_app.get_graph().draw_png().save("./graph_images/langgraph.png")
