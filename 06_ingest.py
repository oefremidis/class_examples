import os

from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_chroma import Chroma



load_dotenv()

PDF_PATH = Path(__file__).parent / "docs" / "codehub_handbook.pdf"
COLLECTION_NAME = "codehubs_docs"

docs = PyPDFLoader(PDF_PATH).load()
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
chunks = splitter.split_documents(docs)

embeddings = AzureOpenAIEmbeddings(
    azure_endpoint=os.environ["AZURE_EMBEDDING_ENDPOINT"],
    api_key=os.environ["AZURE_EMBEDDING_API_KEY"],
    azure_deployment=os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"],
) 

store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    host="localhost",
    port=8000
)


# store.reset_collection()
# store.add_documents(chunks)
# print(f"Added {len(chunks)} chunks to the collection '{COLLECTION_NAME}'")

llm = AzureChatOpenAI(model_name="gpt-4.1-mini", temperature=0.0)
question = "What is the uptime guarantee?"


docs = store.similarity_search(question, k=4)
context = "\n\n".join(d.page_content for d in docs)

messages = [
    (
        "system",
        f"Answer using only this context. If it isn't there, say you don't know.\n\n{context}",
    ),
    ("user", question),
]
print(llm.invoke(messages).content)






