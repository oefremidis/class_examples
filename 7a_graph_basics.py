from dotenv import load_dotenv
from langchain_neo4j import Neo4jGraph

load_dotenv()

# Connect (NEO4J_URI / NEO4J_USERNAME / NEO4J_PASSWORD from .env). See it at http://localhost:7474
graph = Neo4jGraph()

# Nodes = things (:Plan), properties = {price_eur: 79}, relationships = -[:HAS_FEATURE]->
graph.query("MATCH (n) DETACH DELETE n")  # start empty
graph.query("""
CREATE (team:Plan {name: "Team", price_eur: 79})
CREATE (enterprise:Plan {name: "Enterprise", price_eur: 1200})
CREATE (sso:Feature {name: "Single sign-on"})
CREATE (migration:Feature {name: "Region migration"})

CREATE (team)-[:HAS_FEATURE]->(migration)
CREATE (enterprise)-[:HAS_FEATURE]->(migration)
CREATE (enterprise)-[:HAS_FEATURE]->(sso)
""")

# Query = draw the pattern you're looking for.
print(graph.query("""
MATCH (p:Plan)-[:HAS_FEATURE]->(:Feature {name: "Region migration"})
RETURN p.name AS plan, p.price_eur AS price
"""))
