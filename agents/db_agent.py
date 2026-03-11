"""
DB Agent — queries the employee SQLite database.
Wraps 3 internal tools (get_employee, get_manager, search_employees)
behind a single tool for the main agent.
"""
import os
import sys
import sqlite3

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from langchain_core.tools import tool
from langchain_mistralai import ChatMistralAI
from langgraph.prebuilt import create_react_agent
from config import DB_PATH, MISTRAL_MODEL, MISTRAL_TEMPERATURE
from agents.utils import run_subagent


def _query_db(sql: str, params: tuple = ()) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(sql, params)
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def _format_employee(emp: dict) -> str:
    manager = emp["manager_name"] or "Aucun (poste de direction)"
    return (
        f"- Nom: {emp['name']}\n"
        f"  Role: {emp['role']}\n"
        f"  Departement: {emp['department']}\n"
        f"  Email: {emp['email']}\n"
        f"  Telephone: {emp['phone']}\n"
        f"  Manager: {manager}"
    )


@tool
def get_employee(name: str) -> str:
    """Obtenir les informations completes d'un employe par son nom.

    Args:
        name: Le nom (ou partie du nom) de l'employe a rechercher.
    """
    results = _query_db(
        "SELECT name, role, department, email, manager_name, phone FROM employees WHERE name LIKE ?",
        (f"%{name}%",),
    )
    if not results:
        return f"Aucun employe trouve avec le nom '{name}'."
    return "\n".join(_format_employee(emp) for emp in results)


@tool
def get_manager(employee_name: str) -> str:
    """Trouver le manager d'un employe donne.

    Args:
        employee_name: Le nom de l'employe dont on cherche le manager.
    """
    results = _query_db(
        "SELECT manager_name FROM employees WHERE name LIKE ?",
        (f"%{employee_name}%",),
    )
    if not results:
        return f"Employe '{employee_name}' non trouve dans la base."

    manager_name = results[0]["manager_name"]
    if not manager_name:
        return f"{employee_name} n'a pas de manager (poste de direction)."

    manager_info = _query_db(
        "SELECT name, role, department, email, phone FROM employees WHERE name = ?",
        (manager_name,),
    )
    if manager_info:
        m = manager_info[0]
        return (
            f"Le manager de {employee_name} est {m['name']}.\n"
            f"- Role: {m['role']}\n"
            f"- Departement: {m['department']}\n"
            f"- Email: {m['email']}\n"
            f"- Telephone: {m['phone']}"
        )
    return f"Le manager de {employee_name} est {manager_name}."


@tool
def search_employees(query: str) -> str:
    """Rechercher des employes par nom, role, departement ou email.

    Args:
        query: Terme de recherche.
    """
    results = _query_db(
        "SELECT name, role, department, email, phone FROM employees "
        "WHERE name LIKE ? OR role LIKE ? OR department LIKE ? OR email LIKE ?",
        (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"),
    )
    if not results:
        return f"Aucun resultat pour '{query}'."

    lines = [f"Resultats pour '{query}' ({len(results)} employe(s)) :"]
    for emp in results:
        lines.append(f"- {emp['name']} | {emp['role']} | {emp['department']} | {emp['email']} | {emp['phone']}")
    return "\n".join(lines)


_db_agent = create_react_agent(
    model=ChatMistralAI(model=MISTRAL_MODEL, temperature=MISTRAL_TEMPERATURE),
    tools=[get_employee, get_manager, search_employees],
    prompt=(
        "Tu es un agent specialise dans l'acces a la base de donnees des employes de TechCorp France. "
        "Tu disposes de 3 outils pour chercher des employes, trouver des managers, "
        "et obtenir des informations sur les employes. "
        "Reponds toujours en francais. Sois precis et concis."
    ),
)


# Single tool exposed to the main agent
@tool
def query_employee_database(question: str) -> str:
    """Acceder a la base de donnees des employes pour trouver des informations.

    Utilise cet outil quand l'utilisateur demande :
    - Qui est le manager de quelqu'un
    - Les coordonnees d'un employe (email, telephone)
    - Trouver un employe specifique ou un contact RH
    - Les roles et la structure d'equipe

    Args:
        question: La question sur les employes a resoudre via la base de donnees.
    """
    return run_subagent(_db_agent, question)
