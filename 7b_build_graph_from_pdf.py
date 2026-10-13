from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_neo4j import Neo4jGraph
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel

load_dotenv()

PDF_PATH = Path(__file__).parent / "docs" / "codehub_handbook.pdf"

graph = Neo4jGraph()
llm = AzureChatOpenAI(model_name="gpt-4.1-mini", temperature=0.0)


# 1. The shape we want back from the LLM: (plan)-[relation]->(target).
#    We fix the allowed plans and relations. Left free, the LLM invents ~150 relation types
#    and duplicates like "Team" / "Team plan" / "Team customers", and the graph becomes unqueryable.
class Relation(BaseModel):
    plan: Literal["Hobby", "Starter", "Team", "Enterprise"]
    relation: Literal[
        "COSTS", "HAS_FEATURE", "SUPPORTED_VIA", "P1_RESPONSE_TIME", "UPTIME_GUARANTEE"
    ]
    target: str


class Relations(BaseModel):
    relations: list[Relation]


extractor = llm.with_structured_output(Relations)

graph.query("MATCH (n) DETACH DELETE n")  # start empty, so re-running doesn't duplicate

# 2. For each PDF page: the LLM finds the relationships, we store them in Neo4j.
for page in PyPDFLoader(PDF_PATH).load():
    result = extractor.invoke(
        [
            (
                "system",
                "Extract facts about the CodeHub plans that are written explicitly in this text.\n"
                "Never guess. If the text has no such facts, return an empty list.\n"
                "Keep targets short, e.g. 'EUR 79', 'Region migration', '1 hour'.",
            ),
            ("user", page.page_content),
        ]
    )

    for r in result.relations:
        print(f"({r.plan})-[{r.relation}]->({r.target})")
        # A relationship type can't be a query parameter, so it goes in the query text
        # (safe here: Literal above only allows our 5 names).
        graph.query(
            f"MERGE (p:Plan {{name: $plan}}) MERGE (t:Entity {{name: $target}}) MERGE (p)-[:{r.relation}]->(t)",
            {"plan": r.plan, "target": r.target},
        )

# 3. Look at it: http://localhost:7474 and run  MATCH (n) RETURN n
print(graph.query("MATCH ()-[r]->() RETURN type(r) AS relation, count(*) AS count"))
