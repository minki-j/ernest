from varname import nameof as n
from langgraph.graph import END, StateGraph
from langchain_core.runnables import RunnablePassthrough

from app.langchain.schema import StateType
from app.schemas.schemas import State, User, Review, Report
from app.langchain.utils.converters import to_path_map

from app.langchain.nodes.llm.generate import generate_reply
from app.langchain.subgraphs.middle_of_chat.gather_context.graph import gather_context
from app.langchain.nodes.llm.criticize import reflection
from app.langchain.nodes.llm.plan import plan_instruction
from app.langchain.conditional_edges.llm.routers import moc_router
from app.langchain.subgraphs.middle_of_chat.extract.graph import extract

g = StateGraph(StateType)
g.set_entry_point("entry")

g.add_node("entry", RunnablePassthrough())
g.add_edge("entry", n(extract))

g.add_node(n(extract), extract)
g.add_edge(n(extract), n(moc_router))

g.add_node(n(moc_router), RunnablePassthrough())
g.add_conditional_edges(
    n(moc_router),
    moc_router,
    to_path_map(
        [
            n(gather_context),
            n(plan_instruction),
            "end_router",
        ],
    ),
)

g.add_node(n(gather_context), gather_context)
g.add_edge(n(gather_context), n(plan_instruction))
g.add_node(n(plan_instruction), plan_instruction)
g.add_edge(n(plan_instruction), n(moc_router))

g.add_node("end_router", RunnablePassthrough())
g.add_edge("end_router", n(reflection))

g.add_node(n(reflection), RunnablePassthrough())
g.add_conditional_edges(
    n(reflection),
    reflection,
    to_path_map(
        [
            n(moc_router),  # loop back
            n(generate_reply),  # exit
        ]
    ),
)

g.add_node(n(generate_reply), generate_reply)
g.add_edge(n(generate_reply), END)

middle_of_chat = g.compile()

# with open("middle_of_chat.png", "wb") as f:
#     f.write(middle_of_chat.get_graph().draw_png())
