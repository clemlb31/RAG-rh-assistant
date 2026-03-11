"""RAG tool — retrieves relevant HR docs and generates an answer with sources."""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from langchain_core.tools import tool
from langchain_mistralai import ChatMistralAI
from config import MISTRAL_MODEL, MISTRAL_TEMPERATURE, RAG_TOP_K
from rag.vectorstore import search_documents


def _format_context(docs) -> tuple[str, list[str]]:
    """Turn retrieved docs into a prompt-ready context string + list of unique source titles."""
    parts = []
    titles = []
    for doc in docs:
        title = doc.metadata.get("title", "Inconnu")
        titles.append(title)
        parts.append(f"[Source: {title}]\n{doc.page_content}")
    return "\n\n".join(parts), list(set(titles))


@tool
def search_hr_policy(question: str) -> str:
    """Recherche dans la base de connaissances RH de l'entreprise et retourne une reponse.

    Utilise cet outil quand l'utilisateur pose des questions sur :
    - La mutuelle et la couverture sante
    - Les horaires de travail et le pointage
    - Le teletravail et ses modalites
    - Les conges et absences (conges payes, RTT, conges speciaux)
    - Les avantages sociaux (tickets restaurant, transport, epargne, sport, formation)
    - La securite informatique (mots de passe, VPN, regles IT)
    - L'onboarding et la premiere semaine

    Args:
        question: La question RH a laquelle repondre.
    """
    docs = search_documents(question, k=RAG_TOP_K)
    if not docs:
        return "Aucun document pertinent trouve dans la base de connaissances."

    context, source_titles = _format_context(docs)

    llm = ChatMistralAI(model=MISTRAL_MODEL, temperature=MISTRAL_TEMPERATURE)
    prompt = f"""Tu es un assistant RH pour TechCorp France.
Reponds a la question en te basant UNIQUEMENT sur les documents fournis ci-dessous.
Si l'information n'est pas dans les documents, dis-le clairement.
Cite les sources (titres des documents) dans ta reponse.
Reponds en francais de maniere claire et structuree.

Documents:
{context}

Question: {question}

Reponse:"""

    response = llm.invoke(prompt)
    return f"{response.content}\n\n[Sources consultees: {', '.join(source_titles)}]"
