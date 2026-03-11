"""Execution tracing — captures tool calls and results for the Gradio debug panel."""
import re
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ToolCallTrace:
    agent_name: str
    tool_name: str
    tool_args: dict
    tool_result: str
    timestamp: str
    internal_tools: list[str] = field(default_factory=list)
    rag_sources: list[str] = field(default_factory=list)


@dataclass
class ExecutionTrace:
    query: str
    steps: list[ToolCallTrace] = field(default_factory=list)
    final_answer: str = ""
    start_time: str = ""
    end_time: str = ""

    def add_step(self, agent_name: str, tool_name: str, tool_args: dict, tool_result: str,
                 rag_sources: list[str] | None = None, internal_tools: list[str] | None = None):
        self.steps.append(ToolCallTrace(
            agent_name=agent_name,
            tool_name=tool_name,
            tool_args=tool_args,
            tool_result=tool_result[:1000],  # keep it short for the UI
            timestamp=datetime.now().strftime("%H:%M:%S"),
            internal_tools=internal_tools or [],
            rag_sources=rag_sources or [],
        ))

    def format_trace_markdown(self) -> str:
        if not self.steps:
            return "*Aucun outil appele pour cette requete.*"

        lines = ["### Trace d'execution\n"]

        for i, step in enumerate(self.steps, 1):
            lines.append(f"**Etape {i}** `{step.timestamp}`\n")
            lines.append(f"- **Agent** : `{step.agent_name}`")
            lines.append(f"- **Outil** : `{step.tool_name}`")

            args_str = ", ".join(f"{k}={repr(v)}" for k, v in step.tool_args.items())
            lines.append(f"- **Arguments** : `{args_str}`")

            if step.internal_tools:
                lines.append(f"- **Outils internes** : `{' -> '.join(step.internal_tools)}`")

            if step.rag_sources:
                lines.append(f"- **Sources RAG** : {', '.join(step.rag_sources)}")

            # Show a trimmed preview, strip internal metadata
            preview = step.tool_result[:300]
            preview = re.sub(r"\[Internal tools:.*?\]", "", preview).strip()
            preview = re.sub(r"\[Sources consultees:.*?\]", "", preview).strip()
            if len(step.tool_result) > 300:
                preview += "..."
            lines.append(f"- **Resultat** : {preview}")
            lines.append("")

        # Summary chain at the bottom
        chain_parts = []
        for s in self.steps:
            if s.internal_tools:
                chain_parts.append(f"{s.agent_name} -> {', '.join(s.internal_tools)}")
            else:
                chain_parts.append(f"{s.agent_name}/{s.tool_name}")

        lines.append("---")
        lines.append(f"**Chaine d'appels** : {' -> '.join(chain_parts)}")

        if self.start_time and self.end_time:
            lines.append(f"\n**Duree** : {self.start_time} -> {self.end_time}")

        return "\n".join(lines)
