from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command


class State(TypedDict):
    ticket: str
    reply: str


def route(state: State) -> Command[Literal["billing", "general"]]:
    """Decide which node runs next."""
    if "charged" in state["ticket"]:
        return Command(goto="billing")
    return Command(goto="general")


def billing(state: State) -> dict:
    return {"reply": "We will refund you."}


def general(state: State) -> dict:
    return {"reply": "Thanks, we will look into it."}


graph = StateGraph(State)

graph.add_node("route", route)
graph.add_node("billing", billing)
graph.add_node("general", general)

graph.add_edge(START, "route")
graph.add_edge("billing", END)
graph.add_edge("general", END)

app = graph.compile()

print(app.invoke({"ticket": "I was charged twice"})["reply"])
print(app.invoke({"ticket": "The app is slow"})["reply"])
