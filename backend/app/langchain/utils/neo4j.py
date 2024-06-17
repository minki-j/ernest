from neo4j import GraphDatabase
import os

URI = os.getenv("NEO4J_URL")
AUTH = ("neo4j", os.getenv("NEO4J_PASSWORD"))

def get_neo4j_driver():
    neo4j_driver = GraphDatabase.driver(URI, auth=AUTH)
    neo4j_driver.verify_connectivity()
    return neo4j_driver