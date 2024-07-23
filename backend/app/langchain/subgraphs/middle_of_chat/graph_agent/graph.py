from typing import Annotated, TypedDict
from varname import nameof as n
from langgraph.graph import END, StateGraph
from langchain_core.runnables import RunnablePassthrough

from app.langchain.schema import StateType
from app.langchain.schema import Documents
from app.schemas.schemas import State, User, Review, Report
from app.langchain.utils.converters import to_path_map
from app.langchain.nodes.non_llm.neo4j_graph_query import get_other_reviews_from_knowlege_graph
from app.langchain.nodes.llm.generate import generate_reply_refering_other_reviews

g = StateGraph(StateType)
g.set_entry_point("entry")

g.add_node("entry", RunnablePassthrough())
g.add_edge("entry", n(get_other_reviews_from_knowlege_graph))

g.add_node(n(get_other_reviews_from_knowlege_graph), get_other_reviews_from_knowlege_graph)
g.add_edge(n(get_other_reviews_from_knowlege_graph), n(generate_reply_refering_other_reviews))

g.add_node(
    n(generate_reply_refering_other_reviews), generate_reply_refering_other_reviews
)
g.add_edge(n(generate_reply_refering_other_reviews), END)

graph_agent = g.compile()
