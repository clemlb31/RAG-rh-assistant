# Assistant d'Onboarding TechCorp France

Assistant RH intelligent pour l'accueil des nouveaux employés chez TechCorp France. L'application utilise un système multi-agents orchestré par LangGraph, couplé à un module RAG (Retrieval-Augmented Generation) pour répondre aux questions des collaborateurs sur les politiques RH, l'annuaire des employés, la messagerie et la gestion de réunions.

## Table des matières

- [Lancement de l'application](#lancement-de-lapplication)
- [Fonctionnalites](#fonctionnalites)
- [Donnees](#donnees)
- [Architecture et fonctionnement detaille](#architecture-et-fonctionnement-detaille)

---

## Lancement de l'application

### Prérequis

- Python 3.8+
- Une clé API Mistral AI

### Installation

```bash
# 1. Se placer dans le répertoire du projet
cd projet_nlp

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Configurer la clé API Mistral dans le fichier .env
# Créer ou modifier le fichier .env à la racine du projet :
MISTRAL_API_KEY='votre_clé_api_mistral'

# 4. Initialiser la base de données employés (si besoin)
python data/init_db.py

# 5. Lancer l'application
streamlit run app.py
```

L'application Streamlit démarre sur `http://localhost:8501` et s'ouvre automatiquement dans le navigateur.

> **Note :** L'index FAISS (embeddings des documents RH) est construit automatiquement au premier lancement, puis mis en cache dans `data/faiss_index/` pour les lancements suivants.

---

## Fonctionnalites

### 1. Recherche de politiques RH (RAG)

Posez des questions en langage naturel sur les politiques de l'entreprise. Le module RAG retrouve les documents pertinents dans la base de connaissances et genere une reponse sourcee.

- Mutuelle et couverture sante
- Horaires de travail et pointage
- Politique de teletravail
- Conges et absences
- Avantages sociaux (tickets restaurant, transport, sport, etc.)
- Securite informatique
- Guide d'onboarding (programme de la premiere semaine)

Les sources consultees sont citees a la fin de chaque reponse.

### 2. Annuaire des employes

Interrogez la base de donnees des employes de TechCorp :

- Trouver son manager : *"Qui est mon manager ?"*
- Chercher un contact : *"Je cherche le contact RH pour le teletravail."*
- Rechercher par nom, role ou departement

Une page dediee accessible via la navigation laterale propose une vue en cartes avec filtrage par departement et recherche par nom, role ou email.

### 3. Envoi de messages Slack (simulation)

Envoyez des messages a vos collegues via une simulation Slack :

- *"Envoie un message a mon manager pour lui dire que je suis pret."*
- Confirmation avec identifiant du message, destinataire et horodatage

### 4. Gestion de reunions (simulation)

Verifiez les disponibilites et planifiez des reunions :

- *"Mon manager est-il disponible demain a 10h pour un point de 30 minutes ?"*
- *"Planifie une reunion d'onboarding avec mon manager cette semaine."*
- Proposition de creneaux alternatifs en cas de conflit

### 5. Orchestration multi-agents

L'assistant chaine automatiquement plusieurs outils pour repondre a des requetes complexes :

- *"Qui est mon manager et peux-tu lui envoyer un message pour lui dire que je suis pret ?"*
  -> Recherche du manager dans la BDD, puis envoi du message.

### 6. Interface

- **Selecteur d'employe** : changez l'employe connecte via la sidebar pour simuler l'onboarding d'une autre personne
- **Exemples de questions** : 12 questions pre-redigees affichees au demarrage pour decouvrir les capacites de l'assistant
- **Bouton "Nouvelle conversation"** : reinitialise le chat, accessible en haut a droite de la zone principale
- **Theme clair / sombre** : bascule entre les deux themes via la sidebar, independamment du mode systeme
- **Navigation multi-pages** : pages Assistant et Annuaire accessibles via le menu lateral

### 7. Panneau de debug / trace

Un panneau optionnel (activable via le toggle dans la sidebar) affiche a droite du chat :

- Chaque etape d'execution avec horodatage, agent et outil utilises
- Les arguments passes et le resultat de chaque outil
- Les sources RAG consultees
- La chaine d'appels complete et la duree d'execution

---

## Données

### Documents RH (`data/hr_documents/`)

7 fichiers Markdown constituant la base de connaissances RH :

| Fichier | Contenu |
|---------|---------|
| `onboarding.md` | Programme de la première semaine (Jour 1 à 5), checklist administrative, contacts clés |
| `mutuelle.md` | Couverture santé, cotisations, dentaire, optique, bien-être |
| `horaires.md` | Horaires de travail (35h/semaine), horaires flexibles, heures supplémentaires, pointage |
| `teletravail.md` | Éligibilité, jours autorisés (2-3 jours/semaine, mardi-jeudi), VPN, indemnité |
| `conges.md` | 25 jours de congés/an, RTT, congés spéciaux (maternité, paternité, événements familiaux), arrêt maladie |
| `avantages.md` | Transport, tickets restaurant (Swile), salle de sport, formation, primes, épargne salariale |
| `securite_informatique.md` | Politique de mots de passe, classification des données, règles email/Slack/VPN, RGPD |

Ces documents sont découpés en chunks de 500 caractères (avec 50 caractères de chevauchement), puis indexés dans un store vectoriel FAISS via les embeddings Mistral (`mistral-embed`).

### Base de données employés (`data/employees.db`)

Base SQLite contenant 15 employés fictifs de TechCorp. Initialisée via `data/init_db.py`.

**Schéma :**

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | INTEGER | Clé primaire |
| `name` | TEXT | Nom complet |
| `role` | TEXT | Poste occupé |
| `department` | TEXT | Département |
| `email` | TEXT | Adresse email (unique) |
| `manager_name` | TEXT | Nom du manager |
| `phone` | TEXT | Numéro de téléphone |

L'employé par défaut (utilisateur simulé) est **Jean Dupont**, développeur dans l'équipe Développement, managé par Bob Durand. L'employé connecté peut être changé via le sélecteur dans la sidebar.

### Index vectoriel (`data/faiss_index/`)

Cache local de l'index FAISS. Construit automatiquement au premier lancement à partir des documents RH, puis rechargé depuis le disque pour les lancements suivants.

---

## Architecture et fonctionnement détaillé

### Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────┐
│              Interface Streamlit (app.py)                    │
│  ┌──────────┬──────────────────┬─────────────────────────┐  │
│  │ Sidebar  │  Chat + Exemples │  Panneau trace (toggle) │  │
│  │ Employé  │  (page principale│  (agents, outils, RAG)  │  │
│  │ Debug    │   + annuaire)    │                         │  │
│  └──────────┴──────────────────┴─────────────────────────┘  │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│            Agent Principal (main_agent.py)                   │
│         Orchestrateur ReAct via LangGraph                    │
│    Route les requêtes vers les agents spécialisés            │
└───────┬──────────┬──────────┬──────────┬────────────────────┘
        │          │          │          │
        ▼          ▼          ▼          ▼
   ┌─────────┐ ┌────────┐ ┌────────┐ ┌─────────┐
   │  RAG    │ │  DB    │ │Message │ │Meeting  │
   │ Module  │ │ Agent  │ │ Agent  │ │ Agent   │
   └────┬────┘ └───┬────┘ └───┬────┘ └────┬────┘
        │          │          │           │
        ▼          ▼          ▼           ▼
   ┌──────────┐ ┌──────────┐ ┌────────┐ ┌──────────┐
   │  FAISS   │ │  SQLite  │ │  Log   │ │  Log     │
   │  Index   │ │ employees│ │messages│ │ réunions │
   └──────────┘ └──────────┘ └────────┘ └──────────┘
```

### Stack technique

| Composant | Technologie |
|-----------|-------------|
| LLM | Mistral Small (`mistral-small-latest`), température 0 |
| Embeddings | `mistral-embed` |
| Orchestration | LangGraph (pattern ReAct) |
| Framework LLM | LangChain |
| Recherche vectorielle | FAISS (CPU) |
| Base de données | SQLite |
| Interface web | Streamlit (multi-pages) |
| Configuration | python-dotenv |

### Flux d'exécution détaillé

#### 1. Réception de la requête

L'utilisateur saisit une question dans l'interface Streamlit. Le message et l'historique de conversation sont transmis à l'agent principal via `invoke_with_tracing()`, avec le nom de l'employé sélectionné dans la sidebar.

#### 2. Routage par l'agent principal (`main_agent.py`)

L'agent principal est un agent ReAct créé via `create_react_agent` de LangGraph. Il reçoit un prompt système qui :

- L'identifie comme assistant RH d'onboarding pour TechCorp France
- Lui indique le nom de l'employé connecté (dynamique, sélectionné dans la sidebar)
- Liste les 4 outils disponibles et leurs cas d'usage
- Impose de répondre en français, de refuser les questions hors sujet et de citer ses sources

L'agent analyse la requête et décide quel(s) outil(s) appeler. Pour des requêtes complexes, il enchaîne plusieurs outils séquentiellement.

#### 3. Agents spécialisés

Chaque agent spécialisé est lui-même un sous-agent ReAct avec ses propres outils internes :

**Module RAG** (`rag/rag_tool.py`) :
1. Recherche les 3 chunks les plus similaires à la question dans l'index FAISS
2. Formate ces chunks comme contexte
3. Envoie le contexte + la question au LLM avec instruction de ne répondre qu'à partir du contexte
4. Ajoute la liste des sources consultées à la réponse

**DB Agent** (`agents/db_agent.py`) :
- 3 outils internes : `get_employee(name)`, `get_manager(employee_name)`, `search_employees(query)`
- Requêtes SQL avec support de recherche partielle (LIKE)
- Retourne les informations structurées (nom, rôle, département, email, manager, téléphone)

**Message Agent** (`agents/message_agent.py`) :
- 1 outil interne : `send_message(to, message)`
- Simule l'envoi Slack (pas de vraie intégration)
- Stocke les messages dans un log en mémoire avec ID, horodatage et statut

**Meeting Agent** (`agents/meeting_agent.py`) :
- 2 outils internes : `check_availability(attendees, start, duration_min)`, `schedule_meeting(attendees, title, start, duration_min)`
- Simule la vérification de disponibilité (80% disponible, 20% conflit avec créneaux alternatifs)
- Stocke les réunions planifiées dans un log en mémoire

#### 4. Capture de la trace (`tracing/tracer.py`)

Chaque appel d'outil est capturé dans un objet `ToolCallTrace` contenant :
- L'agent appelé et l'outil utilisé
- Les arguments et le résultat (tronqué à 1000 caractères)
- Les outils internes chaînés
- Les sources RAG consultées
- L'horodatage

L'ensemble forme un `ExecutionTrace` qui est formaté en Markdown pour le panneau de debug.

#### 5. Réponse à l'utilisateur

L'agent principal synthétise les résultats de tous les outils appelés en une réponse cohérente en français, affichée dans le chat Streamlit. Si le mode debug est activé, la trace d'exécution s'affiche dans le panneau latéral.

### Structure des fichiers

```
projet_nlp/
├── app.py                    # Point d'entrée, interface Streamlit (multi-pages)
├── config.py                 # Configuration (modèle, chemins, paramètres RAG)
├── requirements.txt          # Dépendances Python
├── .env                      # Clé API Mistral
├── agents/
│   ├── __init__.py
│   ├── main_agent.py         # Agent orchestrateur (ReAct)
│   ├── db_agent.py           # Agent base de données employés
│   ├── message_agent.py      # Agent envoi de messages Slack
│   ├── meeting_agent.py      # Agent gestion de réunions
│   └── utils.py              # Utilitaire run_subagent()
├── rag/
│   ├── __init__.py
│   ├── loader.py             # Chargement et découpage des documents MD
│   ├── vectorstore.py        # Store vectoriel FAISS (singleton)
│   └── rag_tool.py           # Outil de recherche RAG + génération
├── tracing/
│   ├── __init__.py
│   └── tracer.py             # Classes ExecutionTrace et ToolCallTrace
└── data/
    ├── init_db.py             # Script d'initialisation de la BDD
    ├── employees.db           # Base SQLite (15 employés)
    ├── faiss_index/           # Index FAISS mis en cache
    └── hr_documents/          # 7 documents RH en Markdown
        ├── onboarding.md
        ├── mutuelle.md
        ├── horaires.md
        ├── teletravail.md
        ├── conges.md
        ├── avantages.md
        └── securite_informatique.md
```
