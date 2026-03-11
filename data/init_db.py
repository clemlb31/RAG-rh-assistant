"""Bootstrap script — creates and seeds the employees SQLite database.
Run: python data/init_db.py
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "employees.db")

EMPLOYEES = [
    # (name, role, department, email, manager_name, phone)
    ("Alice Martin", "Directrice Technique", "Direction", "alice.martin@techcorp.fr", None, "01 40 50 60 01"),
    ("Bob Durand", "Chef de Projet", "Developpement", "bob.durand@techcorp.fr", "Alice Martin", "01 40 50 60 10"),
    ("Claire Petit", "Developpeuse Senior", "Developpement", "claire.petit@techcorp.fr", "Bob Durand", "01 40 50 60 11"),
    ("David Moreau", "Developpeur Senior", "Developpement", "david.moreau@techcorp.fr", "Bob Durand", "01 40 50 60 12"),
    ("Jean Dupont", "Developpeur Junior", "Developpement", "jean.dupont@techcorp.fr", "Bob Durand", "01 40 50 60 13"),
    ("Lucas Bernard", "Designer UX", "Developpement", "lucas.bernard@techcorp.fr", "Bob Durand", "01 40 50 60 14"),
    ("Sophie Martin", "Responsable RH", "Ressources Humaines", "sophie.martin@techcorp.fr", "Alice Martin", "01 40 50 60 20"),
    ("Pierre Lefebvre", "Assistant RH", "Ressources Humaines", "pierre.lefebvre@techcorp.fr", "Sophie Martin", "01 40 50 60 21"),
    ("Marie Durand", "Referente Teletravail", "Ressources Humaines", "marie.durand@techcorp.fr", "Sophie Martin", "01 40 50 60 22"),
    ("Emma Leroy", "Data Scientist", "Data", "emma.leroy@techcorp.fr", "Alice Martin", "01 40 50 60 30"),
    ("Thomas Girard", "Responsable IT", "IT", "thomas.girard@techcorp.fr", "Alice Martin", "01 40 50 60 40"),
    ("Julie Roux", "Administratrice Systeme", "IT", "julie.roux@techcorp.fr", "Thomas Girard", "01 40 50 60 41"),
    ("Marc Levy", "DPO", "Juridique", "marc.levy@techcorp.fr", "Alice Martin", "01 40 50 60 50"),
    ("Camille Fontaine", "Chef de Produit", "Produit", "camille.fontaine@techcorp.fr", "Alice Martin", "01 40 50 60 60"),
    ("Nicolas Perrin", "QA Engineer", "Qualite", "nicolas.perrin@techcorp.fr", "Bob Durand", "01 40 50 60 15"),
]


def create_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            department TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            manager_name TEXT,
            phone TEXT
        )
    """)
    cursor.executemany(
        "INSERT INTO employees (name, role, department, email, manager_name, phone) VALUES (?, ?, ?, ?, ?, ?)",
        EMPLOYEES,
    )
    conn.commit()
    conn.close()
    print(f"DB created at {DB_PATH} ({len(EMPLOYEES)} employees)")


if __name__ == "__main__":
    create_db()
