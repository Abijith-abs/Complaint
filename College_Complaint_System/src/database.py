"""database.py - all SQLite code lives here (Module 5: Database Management)."""
import os
import sqlite3
from datetime import date

# The database file lives in the "data" folder, next to "src".
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(PROJECT_DIR, "data", "complaints.db")
STATUSES = ["Pending", "In Progress", "Resolved"]
CATEGORIES = ["Electrical", "Plumbing", "Furniture", "Computer Lab", "Fans / Lights", "Other"]


def get_connection(db_file=DB_FILE):
    """Open a connection to the database file (it is created if missing)."""
    os.makedirs(os.path.dirname(os.path.abspath(db_file)), exist_ok=True)
    return sqlite3.connect(db_file)


def create_table(db_file=DB_FILE):
    """Create the complaints table the first time the app runs."""
    with get_connection(db_file) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS complaints (
                   id            INTEGER PRIMARY KEY AUTOINCREMENT,
                   submitted_by  TEXT NOT NULL,
                   category      TEXT NOT NULL,
                   description   TEXT NOT NULL,
                   submit_date   TEXT NOT NULL,
                   status        TEXT NOT NULL DEFAULT 'Pending'
               )"""
        )


def add_complaint(submitted_by, category, description, db_file=DB_FILE):
    """Insert a new complaint. Status is always 'Pending'. Returns the new ID."""
    submitted_by, description = submitted_by.strip(), description.strip()
    if not submitted_by or not description:
        raise ValueError("Name and description cannot be empty.")
    with get_connection(db_file) as conn:
        cur = conn.execute(
            "INSERT INTO complaints (submitted_by, category, description, submit_date, status) "
            "VALUES (?, ?, ?, ?, 'Pending')",
            (submitted_by, category, description, date.today().isoformat()),
        )
        return cur.lastrowid


def get_complaints_by_user(submitted_by, db_file=DB_FILE):
    """Return all complaints submitted by one person (newest first)."""
    with get_connection(db_file) as conn:
        return conn.execute(
            "SELECT id, category, description, submit_date, status FROM complaints "
            "WHERE LOWER(submitted_by) = LOWER(?) ORDER BY id DESC",
            (submitted_by.strip(),),
        ).fetchall()


def get_all_complaints(status=None, db_file=DB_FILE):
    """Return every complaint (optionally only one status) - used by the admin."""
    sql = "SELECT id, submitted_by, category, description, submit_date, status FROM complaints"
    params = ()
    if status:
        sql += " WHERE status = ?"
        params = (status,)
    with get_connection(db_file) as conn:
        return conn.execute(sql + " ORDER BY id DESC", params).fetchall()


def update_status(complaint_id, new_status, db_file=DB_FILE):
    """Change a complaint's status. Returns True if a row was updated."""
    if new_status not in STATUSES:
        raise ValueError(f"Status must be one of {STATUSES}")
    with get_connection(db_file) as conn:
        cur = conn.execute(
            "UPDATE complaints SET status = ? WHERE id = ?", (new_status, complaint_id)
        )
        return cur.rowcount == 1
