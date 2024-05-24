from varname import nameof as n
from langgraph.graph import END, StateGraph
from langchain_core.runnables import RunnablePassthrough

from app.langchain.schema import StateType
from app.schemas.schemas import State, User, Review, Report
from app.langchain.utils.converters import to_path_map

from app.langchain.nodes.llm.plan import plan_instruction

g = StateGraph(StateType)
g.set_entry_point("entry")

g.add_node("entry", RunnablePassthrough())
g.add_edge("entry", n(plan_instruction))

g.add_node(n(plan_instruction), plan_instruction)
g.add_edge(n(plan_instruction), END)

plan_instruction = g.compile()
