from ...utils.neo4j import get_neo4j_driver
from varname import nameof as n
from typing import Literal

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field

from app.langchain.schema import Documents
from app.schemas.schemas import State, Role, Message, StateItem

import time

def get_other_reviews_from_knowlege_graph(state: dict[str, Documents]):
    print("\n==>> get_other_reviews_from_knowlege_graph")
    documents = state["documents"]

    vendor_name = documents.vendor.name

    query = f"""
    MATCH (s:Vendor {{name: "{vendor_name.lower()}"}})-[*1..2]-(t:Topic)
    RETURN t AS topic
    """
    neo4j_driver = get_neo4j_driver()
    with neo4j_driver.session(database="neo4j") as session:
        result = session.run(query)
        result_dict = []
        for record in result:
            record_dict = {key: value for key, value in record["topic"].items()}
            result_dict.append(record_dict)
        if len(result_dict) > 0:
            print("---------Neo4j query result-----------")
            print("Total number of nodes: ", len(result_dict))
            print("Example node: ", result_dict[0])
            print("-------------------------------------")
            documents.state["topic_types_from_KG"] = result_dict
        else: 
            documents.state["topic_types_from_KG"] = None

        return {"documents": documents}
