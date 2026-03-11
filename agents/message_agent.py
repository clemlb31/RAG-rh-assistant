"""
Message Agent — simulates sending Slack messages.
"""
import os
import sys
import uuid
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from langchain_core.tools import tool
from langchain_mistralai import ChatMistralAI
from langgraph.prebuilt import create_react_agent
from config import MISTRAL_MODEL, MISTRAL_TEMPERATURE
from agents.utils import run_subagent

# In-memory log for debugging
message_log: list[dict] = []


@tool
def send_message(to: str, message: str) -> str:
    """Envoyer un message Slack a un collegue.

    Args:
        to: Le nom ou l'adresse email du destinataire.
        message: Le contenu du message a envoyer.
    """
    msg_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    message_log.append({
        "id": msg_id,
        "to": to,
        "message": message,
        "timestamp": timestamp,
        "status": "delivered",
    })

    return (
        f"Message envoye avec succes !\n"
        f"- ID: MSG-{msg_id}\n"
        f"- Destinataire: {to}\n"
        f"- Message: {message}\n"
        f"- Heure: {timestamp}\n"
        f"- Statut: Delivre"
    )


_message_agent = create_react_agent(
    model=ChatMistralAI(model=MISTRAL_MODEL, temperature=MISTRAL_TEMPERATURE),
    tools=[send_message],
    prompt=(
        "Tu es un agent specialise dans l'envoi de messages Slack chez TechCorp France. "
        "Utilise l'outil send_message pour envoyer des messages aux collegues. "
        "Confirme toujours l'envoi avec les details (destinataire, contenu). "
        "Reponds en francais."
    ),
)


@tool
def send_slack_message(request: str) -> str:
    """Envoyer un message Slack a un collegue.

    Utilise cet outil quand l'utilisateur veut :
    - Envoyer un message a quelqu'un (manager, collegue, RH)
    - Notifier quelqu'un de quelque chose

    Args:
        request: Description de qui contacter et quel message envoyer.
    """
    return run_subagent(_message_agent, request)
