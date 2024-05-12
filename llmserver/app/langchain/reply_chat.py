from langgraph.graph import END, StateGraph
from app.langchain.states.document_state import DocumentState
from app.langchain.nodes.decide import decide_next_question
from app.langchain.nodes.generate import (
    generate_answer_with_new_msg,
    generate_reply,
    generate_new_q_for_current_topic,
)
from app.langchain.nodes.check import (
    check_relevant_question,
    check_to_pick_new_question,
    check_enoughness_score,
    check_enoughness_threshold,
)

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

graph.add_node("check_relevant_question", check_relevant_question)
graph.add_conditional_edges("check_relevant_question", check_to_pick_new_question)

graph.add_node("generate_answer_with_new_msg", generate_answer_with_new_msg)
graph.add_edge("generate_answer_with_new_msg", "check_enoughness_score")

graph.add_node("check_enoughness_score", check_enoughness_score)
graph.add_conditional_edges(
    "check_enoughness_score", check_enoughness_threshold
)

graph.add_node("decide_next_question", decide_next_question)
graph.add_edge("decide_next_question", "generate_reply")

graph.add_node("generate_new_q_for_current_topic", generate_new_q_for_current_topic)
graph.add_edge("generate_new_q_for_current_topic", "generate_reply")

graph.add_node("generate_reply", generate_reply)
graph.add_edge("generate_reply", END)

graph.set_entry_point("check_relevant_question")
langgraph_app = graph.compile()

# visualize the graph
# langgraph_app.get_graph().draw_png().save("./graph_images/langgraph.png")
