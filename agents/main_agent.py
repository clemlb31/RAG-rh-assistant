"""
Main Agent — orchestrates sub-agents and RAG to answer user queries.
Streams the execution to build a trace for the debug panel.
"""
import os
import sys
import re
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from langchain_mistralai import ChatMistralAI
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.prebuilt import create_react_agent
from config import MISTRAL_MODEL, MISTRAL_TEMPERATURE, DEFAULT_EMPLOYEE_NAME
from agents.db_agent import query_employee_database
from agents.message_agent import send_slack_message
from agents.meeting_agent import manage_meetings
from rag.rag_tool import search_hr_policy
from tracing.tracer import ExecutionTrace

TOOLS = [search_hr_policy, query_employee_database, send_slack_message, manage_meetings]

SYSTEM_PROMPT_TEMPLATE = """Tu es un assistant d'onboarding RH pour TechCorp France.
Tu aides les nouveaux employes pendant leur premiere semaine dans l'entreprise.

Le nouvel employe que tu assistes s'appelle {employee_name}.

Tu disposes de 4 outils :
1. search_hr_policy : pour les questions sur la mutuelle, les horaires, le teletravail, les conges, les avantages sociaux, la securite informatique et l'onboarding.
2. query_employee_database : pour trouver des informations sur les employes (manager, email, role, departement).
3. send_slack_message : pour envoyer des messages Slack aux collegues.
4. manage_meetings : pour verifier la disponibilite et planifier des reunions.

Regles importantes :
- Reponds TOUJOURS en francais.
- Utilise les outils appropriés pour chaque demande. N'invente pas d'informations.
- Si la question n'est PAS liee a l'onboarding, aux RH, aux employes ou a l'entreprise, refuse poliment en expliquant que tu es specialise dans l'accompagnement d'onboarding RH.
- Pour les demandes complexes (ex: trouver le manager ET lui envoyer un message), enchaine les outils dans le bon ordre.
- Cite tes sources quand tu utilises des informations de la base de connaissances.
- Sois chaleureux et accueillant, c'est la premiere semaine du nouvel employe !
- Quand on te demande "mon manager", il s'agit du manager de {employee_name}.
"""


def _build_agent(employee_name: str):
    return create_react_agent(
        model=ChatMistralAI(model=MISTRAL_MODEL, temperature=MISTRAL_TEMPERATURE),
        tools=TOOLS,
        prompt=SYSTEM_PROMPT_TEMPLATE.format(employee_name=employee_name),
    )

# Maps tool names to readable agent names for the trace panel
TOOL_AGENT_MAP = {
    "search_hr_policy": "RAG Module",
    "query_employee_database": "DB Agent",
    "send_slack_message": "Message Agent",
    "manage_meetings": "Meeting Agent",
}


def _extract_metadata(text: str, tag: str) -> list[str]:
    """Pull bracketed metadata like [Sources consultees: ...] or [Internal tools: ...] from tool output."""
    match = re.search(rf"\[{tag}: (.+?)\]", text)
    return [s.strip() for s in match.group(1).split(",")] if match else []


def invoke_with_tracing(
    user_message: str,
    chat_history: list[tuple[str, str]] | None = None,
    employee_name: str = DEFAULT_EMPLOYEE_NAME,
) -> tuple[str, ExecutionTrace]:
    """Run the main agent and return (answer, trace) for the UI."""
    agent = _build_agent(employee_name)
    trace = ExecutionTrace(query=user_message, start_time=datetime.now().strftime("%H:%M:%S"))

    # Build message list with conversation history
    messages = []
    if chat_history:
        for user_msg, assistant_msg in chat_history:
            messages.append(("user", user_msg))
            messages.append(("assistant", assistant_msg))
    messages.append(("user", user_message))

    final_answer = ""
    pending_tool_calls = {}  # tool_call_id -> (agent_name, tool_name, tool_args)

    for step in agent.stream({"messages": messages}):
        for _node, output in step.items():
            for msg in output.get("messages", []):
                # Tool call request from the LLM
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    for tc in msg.tool_calls:
                        agent_name = TOOL_AGENT_MAP.get(tc["name"], "Unknown")
                        pending_tool_calls[tc["id"]] = (agent_name, tc["name"], tc["args"])

                # Tool result coming back
                elif isinstance(msg, ToolMessage) and msg.tool_call_id in pending_tool_calls:
                    agent_name, tool_name, tool_args = pending_tool_calls.pop(msg.tool_call_id)
                    trace.add_step(
                        agent_name=agent_name,
                        tool_name=tool_name,
                        tool_args=tool_args,
                        tool_result=msg.content,
                        rag_sources=_extract_metadata(msg.content, "Sources consultees") if tool_name == "search_hr_policy" else [],
                        internal_tools=_extract_metadata(msg.content, "Internal tools"),
                    )

                # Final text answer (no tool calls attached)
                elif isinstance(msg, AIMessage) and msg.content and not getattr(msg, "tool_calls", None):
                    final_answer = msg.content

    trace.final_answer = final_answer
    trace.end_time = datetime.now().strftime("%H:%M:%S")
    return final_answer, trace
