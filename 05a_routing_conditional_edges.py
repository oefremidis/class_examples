# Conditional routing: send a ticket to a different node depending on its text.

from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    ticket: str
    reply: str


def route(state: State) -> Literal["billing", "general"]:
    """Decide which node runs next."""
    if "charged" in state["ticket"]:
        return "billing"
    return "general"


def billing(state: State) -> dict:
    return {"reply": "We will refund you."}


def general(state: State) -> dict:
    return {"reply": "Thanks, we will look into it."}


graph = StateGraph(State)

graph.add_node("billing", billing)
graph.add_node("general", general)

graph.add_conditional_edges(
    START,
    route,
    {"billing": "billing", "general": "general"},  # route's return value -> next node
)
graph.add_edge("billing", END)
graph.add_edge("general", END)

app = graph.compile()

print(app.invoke({"ticket": "I was charged twice"})["reply"])
print(app.invoke({"ticket": "The app is slow"})["reply"])
