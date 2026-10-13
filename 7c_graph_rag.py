from dotenv import load_dotenv
from langchain_neo4j import Neo4jGraph
from langchain_openai import AzureChatOpenAI

load_dotenv()

# Needs the graph from 7b.
graph = Neo4jGraph()
llm = AzureChatOpenAI(model_name="gpt-4.1-mini", temperature=0.0)

question = "Which plans have region migration, and what is their P1 response time?"

# 1. The LLM writes Cypher, knowing only the graph's schema.
#    Entity names came from an LLM (e.g. "Region migration self-service"), so we ask for CONTAINS, not exact names.
messages = [
    (
        "system",
        (
            "Write a Neo4j Cypher query for this schema. Return only the query, no markdown.\n"
            "Match Entity names with toLower(e.name) CONTAINS '...'.\n\n"
            f"{graph.schema}"
        ),
    ),
    ("user", question),
]
cypher = llm.invoke(messages).content
print("[cypher]\n" + cypher)

# 2. Retrieve: run it. We get exact facts back, not text chunks.
rows = graph.query(cypher)
print("\n[rows]", rows)

# 3. Generate: answer from the rows (same as rag_naive.py, with rows instead of chunks).
messages = [
    (
        "system",
        f"Answer using only these results.\n\nQuery:\n{cypher}\n\nResults:\n{rows}",
    ),
    ("user", question),
]
print("\n[answer]", llm.invoke(messages).content)
