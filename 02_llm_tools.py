from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import AzureChatOpenAI

load_dotenv()

llm = AzureChatOpenAI(model="gpt-4.1-mini")


@tool
def get_ticket_count(status: str) -> int:
    """Return how many CodeHub support tickets have the given status."""
    return {"open": 42, "closed": 918}.get(status, 0)


tools_by_name = {"get_ticket_count": get_ticket_count}
llm_with_tools = llm.bind_tools([get_ticket_count])

messages = [HumanMessage("How many open tickets does CodeHub have?")]
response = llm_with_tools.invoke(messages)
# print(response)
# print(response.tool_calls)

if response.tool_calls:
    tool_name = response.tool_calls[0]["name"]
    tool_args = response.tool_calls[0]["args"]
    tool_result = tools_by_name[tool_name].invoke(tool_args)
    print("[Tool result]", tool_result)

    messages.append(response)
    messages.append(
        ToolMessage(content=str(tool_result), tool_call_id=response.tool_calls[0]["id"])
    )

    final_response = llm_with_tools.invoke(messages)
    print("[Final answer]", final_response.content)
