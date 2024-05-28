from varname import nameof as n
from langgraph.graph import END, StateGraph
from langchain_core.runnables import RunnablePassthrough

from app.langchain.schema import StateType
from app.schemas.schemas import State, User, Review, Report
from app.langchain.utils.converters import to_path_map

from app.langchain.nodes.llm.generate import generate_reply
from app.langchain.subgraphs.middle_of_chat.gather_context.graph import gather_context
from app.langchain.subgraphs.middle_of_chat.extract.graph import extract
from app.langchain.nodes.llm.find import (
    find_missing_detail_story_only,
    find_missing_detail_with_reply,
)
from app.langchain.nodes.llm.generate import update_story
from app.langchain.nodes.llm.decide import decide_reply_type
from app.langchain.nodes.llm.pick import pick_best_missing_detail

g = StateGraph(StateType)
g.set_entry_point("entry")

g.add_node("entry", RunnablePassthrough())
g.add_edge("entry", n(extract))

g.add_node(n(extract), RunnablePassthrough())  # pass extract subgraph for now
# g.add_node(n(extract), extract)
g.add_edge(n(extract), n(gather_context))

g.add_node(n(gather_context), gather_context) 
g.add_edge(n(gather_context), n(update_story))

g.add_node(n(update_story), update_story)
g.add_edge(n(update_story), n(find_missing_detail_story_only))
g.add_edge(n(update_story), n(find_missing_detail_with_reply))

g.add_node(n(find_missing_detail_story_only), find_missing_detail_story_only)
g.add_edge(n(find_missing_detail_story_only), n(pick_best_missing_detail))

g.add_node(n(find_missing_detail_with_reply), find_missing_detail_with_reply)
g.add_edge(n(find_missing_detail_with_reply), n(pick_best_missing_detail))

g.add_node(n(pick_best_missing_detail), pick_best_missing_detail)
g.add_edge(n(pick_best_missing_detail), n(generate_reply))

g.add_node(n(generate_reply), generate_reply)
g.add_edge(n(generate_reply), n(decide_reply_type))

g.add_node(n(decide_reply_type), decide_reply_type)
g.add_edge(n(decide_reply_type), END)

middle_of_chat = g.compile()

# with open("middle_of_chat.png", "wb") as f:
#     f.write(middle_of_chat.get_graph().draw_png())
