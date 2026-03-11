"""Streamlit multi-page app — Chat + Debug on main page, Annuaire on second page."""
import os
import sys
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from agents.main_agent import invoke_with_tracing
from config import DEFAULT_EMPLOYEE_NAME, DB_PATH

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TechCorp — Assistant Onboarding RH",
    page_icon="TC",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Theme ────────────────────────────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state["theme"] = "clair"

THEMES = {
    "clair": {
        "bg": "#f7f8fa",
        "bg_secondary": "#ffffff",
        "text": "#1a1a2e",
        "text_muted": "#6b7280",
        "text_light": "#4b5563",
        "border": "#d1d9e6",
        "sidebar_bg": "#f4f7fb",
        "card_bg": "#ffffff",
        "trace_bg": "#f4f7fb",
        "badge_agent_bg": "#dbeafe",
        "badge_agent_text": "#1e40af",
        "badge_tool_bg": "#fef9c3",
        "badge_tool_text": "#854d0e",
        "badge_dept_bg": "#dbeafe",
        "badge_dept_text": "#1e40af",
        "btn_bg": "#ffffff",
        "btn_text": "#1a1a2e",
        "btn_border": "#d1d9e6",
        "btn_hover_bg": "#f0f7ff",
        "btn_hover_border": "#3282b8",
        "btn_hover_text": "#0f4c75",
        "code_color": "#475569",
    },
    "sombre": {
        "bg": "#0f1117",
        "bg_secondary": "#1a1b26",
        "text": "#e2e8f0",
        "text_muted": "#94a3b8",
        "text_light": "#a0aec0",
        "border": "#2d3748",
        "sidebar_bg": "#141620",
        "card_bg": "#1a1b26",
        "trace_bg": "#141620",
        "badge_agent_bg": "#1e3a5f",
        "badge_agent_text": "#7cb3f0",
        "badge_tool_bg": "#422006",
        "badge_tool_text": "#fbbf24",
        "badge_dept_bg": "#1e3a5f",
        "badge_dept_text": "#7cb3f0",
        "btn_bg": "#1a1b26",
        "btn_text": "#e2e8f0",
        "btn_border": "#2d3748",
        "btn_hover_bg": "#1e3a5f",
        "btn_hover_border": "#3282b8",
        "btn_hover_text": "#bbe1fa",
        "code_color": "#a0aec0",
    },
}


def inject_css():
    t = THEMES[st.session_state["theme"]]
    st.markdown(f"""
<style>
    .block-container {{ max-width: 1200px; padding-top: 2.5rem; }}

    /* Override Streamlit CSS variables to match app theme */
    :root, .stApp {{
        --primary-color: #3282b8;
        --background-color: {t["bg"]};
        --secondary-background-color: {t["bg_secondary"]};
        --text-color: {t["text"]};
    }}

    /* Force Streamlit background */
    .stApp {{ background-color: {t["bg"]} !important; }}
    .stApp, .stApp * {{ color: {t["text"]}; }}

    /* Streamlit native components: chat messages */
    .stChatMessage {{
        background-color: {t["bg_secondary"]} !important;
        border-radius: 10px;
    }}
    [data-testid="stChatMessageContent"] p,
    [data-testid="stChatMessageContent"] li,
    [data-testid="stChatMessageContent"] a {{
        color: {t["text"]} !important;
    }}

    /* Info / warning / error boxes */
    [data-testid="stAlert"] {{
        background-color: {t["bg_secondary"]} !important;
        color: {t["text"]} !important;
        border-color: {t["border"]} !important;
    }}
    [data-testid="stAlert"] p {{ color: {t["text"]} !important; }}

    /* Selectbox dropdown */
    .stSelectbox div[data-baseweb="select"] > div {{
        background: {t["bg_secondary"]} !important;
        border-color: {t["border"]} !important;
    }}
    .stSelectbox div[data-baseweb="select"] span {{
        color: {t["text"]} !important;
    }}
    [data-baseweb="popover"] {{
        background-color: {t["bg_secondary"]} !important;
        border-color: {t["border"]} !important;
    }}
    [data-baseweb="menu"] {{
        background-color: {t["bg_secondary"]} !important;
    }}
    [data-baseweb="menu"] li {{
        background-color: {t["bg_secondary"]} !important;
        color: {t["text"]} !important;
    }}
    [data-baseweb="menu"] li:hover {{
        background-color: {t["btn_hover_bg"]} !important;
    }}

    /* Radio buttons */
    .stRadio label span {{ color: {t["text"]} !important; }}

    /* Toggle / checkbox */
    .stCheckbox label span {{ color: {t["text"]} !important; }}

    /* Text input */
    .stTextInput input {{
        background: {t["bg_secondary"]} !important;
        color: {t["text"]} !important;
        border-color: {t["border"]} !important;
    }}

    /* Chat input */
    .stChatInput {{
        background-color: {t["bg"]} !important;
        border-color: {t["border"]} !important;
    }}
    .stChatInput > div {{
        background-color: {t["bg_secondary"]} !important;
        border-color: {t["border"]} !important;
    }}
    .stChatInput textarea {{
        background: {t["bg_secondary"]} !important;
        color: {t["text"]} !important;
        border-color: {t["border"]} !important;
    }}
    .stChatInput button {{
        background-color: {t["bg_secondary"]} !important;
        color: {t["text"]} !important;
    }}

    /* Spinner */
    .stSpinner > div {{ color: {t["text_muted"]} !important; }}

    /* Markdown headings */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {{
        color: {t["text"]} !important;
    }}
    .stMarkdown p, .stMarkdown li {{ color: {t["text"]} !important; }}

    /* Dividers */
    .stDivider {{ border-color: {t["border"]} !important; }}
    hr {{ border-color: {t["border"]} !important; }}

    /* Streamlit header toolbar */
    header[data-testid="stHeader"] {{
        background-color: {t["bg"]} !important;
    }}

    /* Example buttons */
    div[data-testid="stButton"] > button {{
        background: {t["btn_bg"]} !important;
        color: {t["btn_text"]} !important;
        border: 1px solid {t["btn_border"]} !important;
        border-radius: 10px !important;
        font-size: 0.85rem !important;
        padding: 0.7rem 1rem !important;
        text-align: left !important;
        white-space: normal !important;
        line-height: 1.4 !important;
        min-height: auto !important;
        transition: all 0.15s ease;
    }}
    div[data-testid="stButton"] > button:hover {{
        border-color: {t["btn_hover_border"]} !important;
        background: {t["btn_hover_bg"]} !important;
        color: {t["btn_hover_text"]} !important;
    }}

    /* Trace panel */
    .trace-container {{
        background: {t["trace_bg"]};
        border: 1px solid {t["border"]};
        border-radius: 12px;
        padding: 1rem 1.25rem;
        font-size: 0.88rem;
        color: {t["text"]};
    }}
    .trace-step {{
        background: {t["card_bg"]};
        border: 1px solid {t["border"]};
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
    }}
    .trace-step-header {{
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.4rem;
    }}
    .trace-agent-badge {{
        background: {t["badge_agent_bg"]};
        color: {t["badge_agent_text"]};
        padding: 0.15rem 0.5rem;
        border-radius: 4px;
        font-size: 0.78rem;
        font-weight: 600;
    }}
    .trace-tool-badge {{
        background: {t["badge_tool_bg"]};
        color: {t["badge_tool_text"]};
        padding: 0.15rem 0.5rem;
        border-radius: 4px;
        font-size: 0.78rem;
        font-weight: 500;
    }}
    .trace-time {{ color: {t["text_muted"]}; font-size: 0.75rem; margin-left: auto; }}
    .trace-detail {{ font-size: 0.82rem; color: {t["code_color"]}; margin-top: 0.3rem; }}
    .trace-preview {{ font-size: 0.82rem; color: {t["text_muted"]}; margin-top: 0.3rem; white-space: pre-wrap; }}
    .trace-chain {{
        background: #0f4c75;
        color: #ffffff;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        font-size: 0.82rem;
        margin-top: 0.5rem;
    }}

    /* Employee cards (annuaire) */
    .emp-card {{
        background: {t["card_bg"]};
        border: 1px solid {t["border"]};
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.75rem;
    }}
    .emp-card .emp-name {{ font-weight: 600; font-size: 1rem; color: {t["text"]}; }}
    .emp-card .emp-role {{ color: {t["text_muted"]}; font-size: 0.85rem; }}
    .emp-card .emp-dept {{
        background: {t["badge_dept_bg"]};
        color: {t["badge_dept_text"]};
        padding: 0.1rem 0.4rem;
        border-radius: 4px;
        font-size: 0.8rem;
        display: inline-block;
        margin-top: 0.4rem;
    }}
    .emp-card .emp-details {{ margin-top: 0.5rem; font-size: 0.82rem; color: {t["text_light"]}; }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background: {t["sidebar_bg"]};
        border-right: 1px solid {t["border"]};
    }}
    section[data-testid="stSidebar"] * {{ color: {t["text"]}; }}


</style>
""", unsafe_allow_html=True)


# ── Helpers ──────────────────────────────────────────────────────────────────
@st.cache_data
def load_employees() -> list[str]:
    """Load employee names from DB for the selector."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM employees ORDER BY name")
    names = [row[0] for row in cursor.fetchall()]
    conn.close()
    return names


def format_trace_html(trace) -> str:
    """Convert an ExecutionTrace into styled HTML for the debug panel."""
    if not trace or not trace.steps:
        return '<div class="trace-container"><em>Aucun outil appelé pour cette requête.</em></div>'

    import re
    html = '<div class="trace-container">'
    for i, step in enumerate(trace.steps, 1):
        args_str = ", ".join(f"{k}={repr(v)}" for k, v in step.tool_args.items())
        preview = step.tool_result[:300]
        preview = re.sub(r"\[Internal tools:.*?\]", "", preview).strip()
        preview = re.sub(r"\[Sources consultees:.*?\]", "", preview).strip()
        if len(step.tool_result) > 300:
            preview += "…"

        html += f'''
        <div class="trace-step">
            <div class="trace-step-header">
                <span style="font-weight:600;">Étape {i}</span>
                <span class="trace-agent-badge">{step.agent_name}</span>
                <span class="trace-tool-badge">{step.tool_name}</span>
                <span class="trace-time">{step.timestamp}</span>
            </div>
            <div class="trace-detail">
                <strong>Args :</strong> <code>{args_str}</code>
            </div>'''
        if step.internal_tools:
            html += f'<div class="trace-detail"><strong>Outils internes :</strong> {" → ".join(step.internal_tools)}</div>'
        if step.rag_sources:
            html += f'<div class="trace-detail"><strong>Sources RAG :</strong> {", ".join(step.rag_sources)}</div>'
        html += f'<div class="trace-preview">{preview}</div>'
        html += '</div>'

    # Chain summary
    chain_parts = []
    for s in trace.steps:
        if s.internal_tools:
            chain_parts.append(f"{s.agent_name} → {', '.join(s.internal_tools)}")
        else:
            chain_parts.append(f"{s.agent_name}/{s.tool_name}")
    html += f'<div class="trace-chain"><strong>Chaine :</strong> {" → ".join(chain_parts)}'
    if trace.start_time and trace.end_time:
        html += f'&nbsp;&nbsp;|&nbsp;&nbsp;{trace.start_time} → {trace.end_time}'
    html += '</div></div>'
    return html


# ── Example questions ────────────────────────────────────────────────────────
EXAMPLES = [
    {"label": "Mon manager", "prompt": "Je viens d'arriver. Qui est mon manager et peux-tu lui envoyer un message pour lui dire que je suis prêt ?"},
    {"label": "Mutuelle", "prompt": "Comment fonctionne la mutuelle ? Quels sont les niveaux de couverture ?"},
    {"label": "Horaires", "prompt": "Quels sont les horaires de travail ? Y a-t-il des horaires flexibles ?"},
    {"label": "Télétravail", "prompt": "Comment fonctionne le télétravail ? Combien de jours par semaine ?"},
    {"label": "Réunion", "prompt": "Peux-tu vérifier si mon manager est disponible demain à 10h pour un point de 30 minutes et planifier la réunion ?"},
    {"label": "Congés", "prompt": "Combien de jours de congés ai-je par an ? Comment fonctionne la prise de congés ?"},
    {"label": "Avantages", "prompt": "Quels sont les avantages sociaux de l'entreprise ? Tickets restaurant, transport, sport ?"},
    {"label": "Sécurité IT", "prompt": "Quelles sont les règles de sécurité informatique ? Politique de mots de passe ?"},
    {"label": "Onboarding", "prompt": "Quel est le programme de ma première semaine d'onboarding ?"},
    {"label": "Contact RH", "prompt": "Je cherche le contact RH pour le télétravail."},
    {"label": "Message collègue", "prompt": "Peux-tu envoyer un message à Sophie Martin pour lui demander les documents d'onboarding ?"},
    {"label": "Équipe", "prompt": "Qui fait partie de l'équipe Développement ?"},
]


# ── Navigation ───────────────────────────────────────────────────────────────
def page_chat():
    """Main page: Chat + Debug."""

    # Sidebar
    with st.sidebar:
        st.markdown("### Parametres")

        employees = load_employees()
        default_idx = employees.index(DEFAULT_EMPLOYEE_NAME) if DEFAULT_EMPLOYEE_NAME in employees else 0
        selected_employee = st.selectbox(
            "Employe connecte",
            employees,
            index=default_idx,
            help="Changez l'employé pour simuler l'onboarding d'une autre personne",
        )
        st.session_state["employee_name"] = selected_employee

        st.divider()
        debug_mode = st.toggle("Mode Debug / Trace", value=True, help="Affiche la trace d'exécution des agents et outils")
        st.session_state["debug_mode"] = debug_mode

        st.divider()
        theme_choice = st.radio(
            "Theme",
            ["clair", "sombre"],
            index=0 if st.session_state["theme"] == "clair" else 1,
            horizontal=True,
        )
        if theme_choice != st.session_state["theme"]:
            st.session_state["theme"] = theme_choice
            st.rerun()


    # Inject CSS after theme is resolved
    inject_css()

    # Top bar: connected user + reset button
    employee_name = st.session_state.get("employee_name", DEFAULT_EMPLOYEE_NAME)
    top_left, top_right = st.columns([4, 1])
    with top_left:
        st.caption(f"Connecte en tant que **{employee_name}**")
    with top_right:
        if st.button("Nouvelle conversation", use_container_width=True):
            st.session_state["messages"] = []
            st.session_state["last_trace"] = None
            st.rerun()

    # Init session state
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "last_trace" not in st.session_state:
        st.session_state["last_trace"] = None

    # Examples section (shown when no messages yet)
    if not st.session_state["messages"]:
        st.markdown("#### Exemples de questions")
        cols = st.columns(2)
        for i, ex in enumerate(EXAMPLES):
            with cols[i % 2]:
                if st.button(ex["prompt"], key=f"ex_{i}", use_container_width=True):
                    st.session_state["pending_example"] = ex["prompt"]
                    st.rerun()

    # Layout: Chat (left) + Debug (right)
    debug_mode = st.session_state.get("debug_mode", True)

    if debug_mode:
        chat_col, debug_col = st.columns([2, 1])
    else:
        chat_col = st.container()
        debug_col = None

    with chat_col:
        # Display chat history
        for msg in st.session_state["messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Handle pending example
        if "pending_example" in st.session_state:
            prompt = st.session_state.pop("pending_example")
            _handle_user_input(prompt, employee_name)

        # Chat input
        if prompt := st.chat_input("Posez votre question sur l'onboarding, la mutuelle, les horaires…"):
            _handle_user_input(prompt, employee_name)

    # Debug panel
    if debug_mode and debug_col is not None:
        with debug_col:
            st.markdown("#### Trace d'execution")
            trace = st.session_state.get("last_trace")
            if trace:
                st.markdown(format_trace_html(trace), unsafe_allow_html=True)
            else:
                st.info("En attente d'une requête…")


def _handle_user_input(prompt: str, employee_name: str):
    """Process user input: display message, call agent, show response."""
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Réflexion en cours…"):
            try:
                # Build chat history as tuples
                chat_history = []
                msgs = st.session_state["messages"]
                for i in range(0, len(msgs) - 1, 2):
                    if msgs[i]["role"] == "user" and i + 1 < len(msgs) and msgs[i + 1]["role"] == "assistant":
                        chat_history.append((msgs[i]["content"], msgs[i + 1]["content"]))

                answer, trace = invoke_with_tracing(prompt, chat_history, employee_name)
            except Exception as e:
                answer = f"Désolé, une erreur est survenue : {e}"
                trace = None

        st.markdown(answer)

    st.session_state["messages"].append({"role": "assistant", "content": answer})
    st.session_state["last_trace"] = trace
    st.rerun()


def page_annuaire():
    """Employee directory page."""
    # Inject CSS for annuaire page too
    inject_css()

    st.subheader("Annuaire des employes")

    # Theme selector in sidebar for annuaire page too
    with st.sidebar:
        theme_choice = st.radio(
            "Theme",
            ["clair", "sombre"],
            index=0 if st.session_state["theme"] == "clair" else 1,
            horizontal=True,
            key="annuaire_theme",
        )
        if theme_choice != st.session_state["theme"]:
            st.session_state["theme"] = theme_choice
            st.rerun()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT name, role, department, email, phone, manager_name FROM employees ORDER BY department, name")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    # Filters
    col1, col2 = st.columns(2)
    departments = sorted(set(r["department"] for r in rows))
    with col1:
        dept_filter = st.selectbox("Filtrer par département", ["Tous"] + departments)
    with col2:
        search = st.text_input("Rechercher", placeholder="Nom, role, email...")

    filtered = rows
    if dept_filter != "Tous":
        filtered = [r for r in filtered if r["department"] == dept_filter]
    if search:
        q = search.lower()
        filtered = [r for r in filtered if q in r["name"].lower() or q in r["role"].lower() or q in r["email"].lower()]

    st.markdown(f"**{len(filtered)}** employé(s) trouvé(s)")
    st.divider()

    # Display as cards in columns
    cols = st.columns(3)
    for i, emp in enumerate(filtered):
        with cols[i % 3]:
            manager_text = emp["manager_name"] or "—"
            st.markdown(
                f"""
                <div class="emp-card">
                    <div class="emp-name">{emp['name']}</div>
                    <div class="emp-role">{emp['role']}</div>
                    <div><span class="emp-dept">{emp['department']}</span></div>
                    <div class="emp-details">
                        {emp['email']}<br>
                        {emp['phone']}<br>
                        Manager : {manager_text}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ── App entry point ──────────────────────────────────────────────────────────
pg = st.navigation([
    st.Page(page_chat, title="Assistant"),
    st.Page(page_annuaire, title="Annuaire"),
])
pg.run()
