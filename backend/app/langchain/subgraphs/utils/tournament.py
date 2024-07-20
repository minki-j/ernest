from varname import nameof as n

from langgraph.graph import END, StateGraph
from langchain_core.runnables import RunnablePassthrough

from app.langchain.schema import StateType
from app.schemas.schemas import State, User, Review, Report
from app.langchain.utils.converters import to_path_map

from app.langchain.conditional_edges.non_llm.simple_check import is_tournament_complete
from app.langchain.nodes.llm.pick import random_one_on_one_match
from app.langchain.nodes.non_llm.tournament_stage import stage_all_players


g = StateGraph(StateType)
g.set_entry_point("entry")

g.add_node("entry", RunnablePassthrough())
g.add_edge("entry", n(stage_all_players))

g.add_node(n(stage_all_players), stage_all_players)
g.add_edge(n(stage_all_players), n(is_tournament_complete))

g.add_node(n(is_tournament_complete), RunnablePassthrough())
g.add_conditional_edges(
    n(is_tournament_complete),
    is_tournament_complete,
    to_path_map(
        [
            n(random_one_on_one_match),
            "__end__",
        ]
    ),
)

g.add_node(n(random_one_on_one_match), random_one_on_one_match)
g.add_edge(n(random_one_on_one_match), n(is_tournament_complete))

tournament = g.compile()


# with open("graph_imgs/tournament.png", "wb") as f:
#     f.write(tournament.get_graph().draw_mermaid_png())
