from typing import Annotated, TypedDict
from varname import nameof as n
from langgraph.graph import END, StateGraph
from langchain_core.runnables import RunnablePassthrough

from app.langchain.schema import StateType
from app.langchain.schema import Documents
from app.schemas.schemas import State, User, Review, Report
from app.langchain.utils.converters import to_path_map
from app.langchain.nodes.non_llm.neo4j_graph_query import get_topics_for_vendor
from app.langchain.nodes.llm.generate import generate_reply_refering_other_reviews

g = StateGraph(StateType)
g.set_entry_point("entry")

g.add_node("entry", RunnablePassthrough())
g.add_edge("entry", n(get_topics_for_vendor))

g.add_node(n(get_topics_for_vendor), get_topics_for_vendor)
g.add_edge(n(get_topics_for_vendor), n(generate_reply_refering_other_reviews))

g.add_node(
    n(generate_reply_refering_other_reviews), generate_reply_refering_other_reviews
)
g.add_edge(n(generate_reply_refering_other_reviews), "rendezvous")

g.add_node("rendezvous", RunnablePassthrough())
g.add_edge("rendezvous", END)

graph_agent = g.compile()
