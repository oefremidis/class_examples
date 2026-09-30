from typing import TypedDict

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import AzureChatOpenAI
from langgraph.graph import END, START, StateGraph

load_dotenv()

llm = AzureChatOpenAI(model="gpt-4.1-mini")


class State(TypedDict):
    question: str
    answer: str | None


def normalize(state: State) -> dict:
    """Plain function, no LLM -- only updates 'question'; 'answer' is untouched."""
    return {"question": state["question"].strip().rstrip("?") + "?"}


def answer(state: State) -> dict:
    """Reads 'question', writes only 'answer' -- 'question' stays as-is."""
    response = llm.invoke([HumanMessage(state["question"])])
    return {"answer": response.content}


graph = StateGraph(State)
graph.add_node("normalize", normalize)
graph.add_node("answer", answer)
graph.add_edge(START, "normalize")
graph.add_edge("normalize", "answer")
graph.add_edge("answer", END)
app = graph.compile()

result = app.invoke({"question": "  what is the speed of light  ", "answer": None})
print(result)


mermaid = app.get_graph().draw_mermaid()
with open("graph.md", "w", encoding="utf-8") as f:
    f.write("```mermaid\n")
    f.write(mermaid)
    f.write("\n```")
