from langgraph.graph import END, StateGraph
from langchain_core.runnables import RunnablePassthrough

from app.langchain.states.document_state import DocumentState

from app.langchain.conditional_edges.pick_by_llm import is_reply_A_to_Q
from app.langchain.conditional_edges.simple_check import is_next_Q

# from app.langchain.nodes.decide import (

# )
from app.langchain.nodes.generate import (
    generate_reply_for_not_A,
    evaluate_enoughness_score,
)

# from app.langchain.nodes.check import (

# )

passthrough_node = RunnablePassthrough()

# Features to add
# todo: export the report of the survey
# todo: Add purpose of the survey
# todo: Add quantitaive version of question
# todo: conceal PII when asked
# todo: discard previous answer when asked
# todo: add local llama3 model

# Flow engineering
# 1. if there is no previous conversation or no relevant question
#     1.1 pick a question from the list (tool)
# 2. if a relevant question exists
#     2.2 u hhpdate the answer with user's last message
#     2.3 check if the answer is enough
#         2.3.1 if not enough, ask more questions about the current topic
#         2.3.2 if enough, choose the next question

graph = StateGraph(DocumentState)

graph.add_node("start", passthrough_node)
graph.add_conditional_edges("start", is_reply_A_to_Q)

graph.add_node("generate_reply_for_not_A", generate_reply_for_not_A)
graph.add_edge("generate_reply_for_not_A", END)

graph.add_node("evaluate_enoughness_score", evaluate_enoughness_score)
graph.add_edge("evaluate_enoughness_score", END)
# graph.add_conditional_edges("evaluate_enoughness_score", check_enoughness_threshold)

graph.add_node("fork1", passthrough_node)
graph.add_conditional_edges("fork1", is_next_Q)

graph.add_node("pick_next_Q", pick_next_Q)
# graph.add_edge("pick_next_Q", "generate_reply")

# graph.add_node("fork2", passthrough_node)
# graph.add_conditional_edges("fork2", is_enough_Q_in_topic)

# graph.add_node("generate_new_q_for_current_topic", generate_new_q_for_current_topic)
# graph.add_edge("generate_new_q_for_current_topic", "generate_reply")

# graph.add_node("fork3", passthrough_node)
# graph.add_conditional_edges("fork3", is_next_topic)

# graph.add_node("pick_a_Q_in_new_topic", pick_a_Q_in_new_topic)
# graph.add_edge("pick_a_Q_in_new_topic", "generate_reply")

# graph.add_node("end_conversation", end_conversation)
# graph.add_edge("end_conversation", END)

# graph.add_node("generate_Q_reply", generate_reply)
# graph.add_edge("generate_Q_reply", END)

graph.set_entry_point("start")
langgraph_app = graph.compile()

# visualize the graph
# langgraph_app.get_graph().draw_png().save("./graph_images/langgraph.png")
