from typing import Literal
from varname import nameof as n

from app.langchain.schema import Documents
from app.schemas.schemas import State


def stage_all_players(state: dict[str, Documents]):
    print("\n==>> stage_all_players")
    documents = state["documents"]

    options = []

    for _, value in documents.state.missing_details.items():
        options += value

    # print("tournament:", documents.state.tournament)

    documents.state.tournament["players"] = options

    return {"documents": documents}
