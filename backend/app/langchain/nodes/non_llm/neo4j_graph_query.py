from ...utils.neo4j import get_neo4j_driver
from varname import nameof as n
from typing import Literal

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field

from app.langchain.schema import Documents
from app.schemas.schemas import State, Role, Message, StateItem

import time

def get_topics_for_vendor(state: dict[str, Documents]):
    print("\n==>> get_topics_for_vendor")
    documents = state["documents"]

    vendor_name = documents.vendor.name

    query = f"""
    MATCH (s:Salon {{name: "{vendor_name}"}})-[*1..2]-(t:Topic)
    RETURN t AS topic
    """
    neo4j_driver = get_neo4j_driver()
    with neo4j_driver.session(database="neo4j") as session:
        result = session.run(query)
        result_dict = []
        for record in result:
            record_dict = {key: value for key, value in record["topic"].items()}
            result_dict.append(record_dict)

        documents.state["topic_types_from_KG"] = result_dict
        return {"documents": documents}
