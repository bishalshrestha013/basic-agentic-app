"""Bridge between the HTTP layer and the compiled LangGraph agent."""

from collections.abc import AsyncIterator

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from agent.graph import build_graph
from schemas import ChatMessage


def _to_lc_messages(history: list[ChatMessage], message: str) -> list[BaseMessage]:
    messages: list[BaseMessage] = []
    for item in history:
        if item.role == "user":
            messages.append(HumanMessage(content=item.content))
        else:
            messages.append(AIMessage(content=item.content))
    messages.append(HumanMessage(content=message))

    return messages


def run_chat(message: str, history: list[ChatMessage]) -> str:
    """Run the agent to completion and return the final assistant text."""
    graph = build_graph()
    result = graph.invoke({"messages": _to_lc_messages(history, message)})
    final = result["messages"][-1]

    return final.content if isinstance(final.content, str) else str(final.content)


async def stream_chat(
    message: str, history: list[ChatMessage]
) -> AsyncIterator[str]:
    """Yield assistant text tokens as they are generated."""
    graph = build_graph()
    inputs = {"messages": _to_lc_messages(history, message)}

    async for chunk, _metadata in graph.astream(inputs, stream_mode="messages"):
        # Only stream natural-language tokens from the model, not tool-call
        # argument fragments (which arrive with empty content).
        if isinstance(chunk, AIMessage) and isinstance(chunk.content, str):
            if chunk.content:
                yield chunk.content
