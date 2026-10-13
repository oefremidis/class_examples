import os

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_neo4j import Neo4jGraph
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

load_dotenv()

# Needs the chunks in Chroma (ingest.py) and the graph in Neo4j (7b).
embeddings = AzureOpenAIEmbeddings(
    azure_endpoint=os.environ["AZURE_EMBEDDING_ENDPOINT"],
    api_key=os.environ["AZURE_EMBEDDING_API_KEY"],
    azure_deployment=os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"],
)
store = Chroma(collection_name="codehub_docs", embedding_function=embeddings, host="localhost", port=8000)
graph = Neo4jGraph()
llm = AzureChatOpenAI(model_name="gpt-4.1-mini", temperature=0.0)

question = "What do I get with the Team plan?"

# 1. Vector search: the TEXT, exactly like rag_naive.py.
docs = store.similarity_search(question, k=3)
text = "\n\n".join(d.page_content for d in docs)

# 2. Graph: the FACTS about every plan that text mentions.
plans = [row["name"] for row in graph.query("MATCH (p:Plan) RETURN p.name AS name")]
mentioned = [p for p in plans if p in text]
facts = graph.query(
    """
    MATCH (p:Plan)-[r]->(x)
    WHERE p.name IN $plans
    RETURN p.name AS plan, type(r) AS relation, x.name AS target
    """,
    {"plans": mentioned},
)
print("[plans in text]", mentioned)
print("[graph facts]", facts)

# 3. Generate from both.
messages = [
    ("system", f"Answer using only this context.\n\nText:\n{text}\n\nGraph facts:\n{facts}"),
    ("user", question),
]
print("\n[answer]", llm.invoke(messages).content)
