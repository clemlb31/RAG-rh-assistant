"""Shared helper to run sub-agents without duplicating the stream/collect logic everywhere."""

from langchain_core.messages import AIMessage


def run_subagent(agent, question: str) -> str:
    """
    Stream a sub-agent, capture internal tool calls and final answer in one pass.
    Appends [Internal tools: ...] metadata to the answer for tracing.
    """
    answer = ""
    internal_calls = []

    for step in agent.stream({"messages": [("user", question)]}):
        for _node, output in step.items():
            for msg in output.get("messages", []):
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    for tc in msg.tool_calls:
                        internal_calls.append(f"{tc['name']}({tc['args']})")
                elif isinstance(msg, AIMessage) and msg.content and not getattr(msg, "tool_calls", None):
                    answer = msg.content

    if internal_calls:
        answer += f"\n[Internal tools: {', '.join(internal_calls)}]"

    return answer
