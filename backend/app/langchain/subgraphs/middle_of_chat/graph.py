from varname import nameof as n
from langgraph.graph import END, StateGraph
from langchain_core.runnables import RunnablePassthrough

from app.langchain.schema import StateType
from app.schemas.schemas import State, User, Review, Report
from app.langchain.utils.converters import to_path_map

from app.langchain.nodes.llm.generate import generate_reply
from app.langchain.subgraphs.middle_of_chat.gather_context.graph import gather_context
from app.langchain.subgraphs.middle_of_chat.extract.graph import extract
from app.langchain.nodes.llm.find import find_missing_details
from app.langchain.nodes.llm.generate import update_story


g = StateGraph(StateType)
g.set_entry_point("entry")

g.add_node("entry", RunnablePassthrough())
g.add_edge("entry", n(extract))

g.add_node(n(extract), extract)
g.add_edge(n(extract), n(gather_context))

g.add_node(n(gather_context), gather_context)
g.add_edge(n(gather_context), n(update_story))

g.add_node(n(update_story), update_story)
g.add_edge(n(update_story), n(find_missing_details))

g.add_node(n(find_missing_details), find_missing_details)
g.add_edge(n(find_missing_details), n(generate_reply))

g.add_node(n(generate_reply), generate_reply)
g.add_edge(n(generate_reply), END)

middle_of_chat = g.compile()

# with open("middle_of_chat.png", "wb") as f:
#     f.write(middle_of_chat.get_graph().draw_png())
