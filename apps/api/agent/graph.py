"""LangGraph tool-calling agent.

An "agent" node calls the LLM. A conditional edge routes to a ToolNode whenever
the model emits tool calls, then loops back to the agent. When the model
produces a plain text answer, the graph ends.
"""

from functools import lru_cache

from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import MessagesState
from langgraph.prebuilt import ToolNode, tools_condition

from agent.tools import TOOLS
from config import get_settings
from constants import SYSTEM_PROMPT


@lru_cache
def _build_model() -> ChatOpenAI:
    settings = get_settings()
    model = ChatOpenAI(
        model=settings.openai_model,
        temperature=settings.openai_temperature,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        streaming=True,
    )

    return model.bind_tools(TOOLS)


def _agent_node(state: MessagesState) -> dict:
    model = _build_model()
    messages = [SystemMessage(content=SYSTEM_PROMPT), *state["messages"]]
    response = model.invoke(messages)

    return {"messages": [response]}


@lru_cache
def build_graph():
    """Compile and cache the agent graph."""
    builder = StateGraph(MessagesState)
    builder.add_node("agent", _agent_node)
    builder.add_node("tools", ToolNode(TOOLS))

    builder.add_edge(START, "agent")
    builder.add_conditional_edges(
        "agent", tools_condition, {"tools": "tools", END: END}
    )
    builder.add_edge("tools", "agent")

    return builder.compile()
