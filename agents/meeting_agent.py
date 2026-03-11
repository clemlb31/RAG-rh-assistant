"""
Meeting Agent — simulates calendar availability checks and meeting scheduling.
"""
import os
import sys
import uuid
import random
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from langchain_core.tools import tool
from langchain_mistralai import ChatMistralAI
from langgraph.prebuilt import create_react_agent
from config import MISTRAL_MODEL, MISTRAL_TEMPERATURE
from agents.utils import run_subagent

# In-memory log for debugging
meeting_log: list[dict] = []


@tool
def check_availability(attendees: list[str], start: str, duration_min: int) -> str:
    """Verifier la disponibilite calendrier d'une liste de participants a un horaire donne.

    Args:
        attendees: Liste des noms des participants.
        start: Horaire de debut propose (ex: "2026-03-06 10:00").
        duration_min: Duree de la reunion en minutes.
    """
    # 80% chance everyone is free (simulated)
    all_available = random.random() > 0.2

    if all_available:
        return (
            f"Tous les participants sont disponibles :\n"
            f"- Participants: {', '.join(attendees)}\n"
            f"- Creneau: {start} ({duration_min} min)\n"
            f"- Statut: Disponible\n"
            f"Le creneau est libre, vous pouvez planifier la reunion."
        )

    conflict_person = random.choice(attendees)
    return (
        f"Conflit de calendrier detecte :\n"
        f"- {conflict_person} n'est pas disponible a {start}.\n"
        f"- Creneaux alternatifs proposes (meme jour, {duration_min} min) :\n"
        f"  - 14:00 - {14 + duration_min // 60}:{duration_min % 60:02d}\n"
        f"  - 15:30 - {15 + (30 + duration_min) // 60}:{(30 + duration_min) % 60:02d}\n"
        f"  - 16:00 - {16 + duration_min // 60}:{duration_min % 60:02d}"
    )


@tool
def schedule_meeting(attendees: list[str], title: str, start: str, duration_min: int) -> str:
    """Planifier une reunion dans le calendrier.

    Args:
        attendees: Liste des noms des participants.
        title: Titre/sujet de la reunion.
        start: Horaire de debut (ex: "2026-03-06 10:00").
        duration_min: Duree en minutes.
    """
    meeting_id = str(uuid.uuid4())[:8]

    meeting_log.append({
        "id": meeting_id,
        "title": title,
        "attendees": attendees,
        "start": start,
        "duration_min": duration_min,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })

    return (
        f"Reunion planifiee avec succes !\n"
        f"- ID: MTG-{meeting_id}\n"
        f"- Titre: {title}\n"
        f"- Participants: {', '.join(attendees)}\n"
        f"- Horaire: {start} ({duration_min} min)\n"
        f"- Statut: Confirmee\n"
        f"Les invitations ont ete envoyees aux participants."
    )


_meeting_agent = create_react_agent(
    model=ChatMistralAI(model=MISTRAL_MODEL, temperature=MISTRAL_TEMPERATURE),
    tools=[check_availability, schedule_meeting],
    prompt=(
        "Tu es un agent specialise dans la gestion de calendrier chez TechCorp France. "
        "Tu peux verifier la disponibilite des participants et planifier des reunions. "
        "Reponds en francais avec les details de la reunion ou de la disponibilite."
    ),
)


@tool
def manage_meetings(request: str) -> str:
    """Gerer le calendrier : verifier la disponibilite et planifier des reunions.

    Utilise cet outil quand l'utilisateur veut :
    - Verifier si quelqu'un est disponible a un certain horaire
    - Planifier une reunion ou un point avec des collegues

    Args:
        request: Description de la reunion a verifier/planifier (qui, quand, combien de temps, sujet).
    """
    return run_subagent(_meeting_agent, request)
