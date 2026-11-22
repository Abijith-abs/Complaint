"""Simple tests for database.py. Run from the project folder with:  python tests/test_database.py
Uses a temporary database so real data is never touched."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

import database as db

path = os.path.join(tempfile.mkdtemp(), "test.db")
results = []


def check(name, condition):
    results.append((name, "PASS" if condition else "FAIL"))


db.create_table(path)
cid = db.add_complaint("Asha", "Electrical", "Fan not working in Room 101", path)
check("T1 add complaint returns an ID", cid == 1)
check("T2 new complaint is Pending", db.get_all_complaints(db_file=path)[0][5] == "Pending")
db.add_complaint("Ravi", "Plumbing", "Tap leaking in washroom", path)
check("T3 user sees only own complaints", len(db.get_complaints_by_user("asha", path)) == 1)
check("T4 admin sees all complaints", len(db.get_all_complaints(db_file=path)) == 2)
check("T5 update to In Progress", db.update_status(1, "In Progress", path))
check("T6 update to Resolved", db.update_status(1, "Resolved", path))
check("T7 user sees updated status", db.get_complaints_by_user("Asha", path)[0][4] == "Resolved")
check("T8 filter by status", len(db.get_all_complaints("Pending", path)) == 1)
try:
    db.update_status(1, "Done", path)
    check("T9 invalid status rejected", False)
except ValueError:
    check("T9 invalid status rejected", True)
try:
    db.add_complaint("Asha", "Other", "   ", path)
    check("T10 empty description rejected", False)
except ValueError:
    check("T10 empty description rejected", True)
check("T11 unknown ID not updated", db.update_status(999, "Resolved", path) is False)

for name, outcome in results:
    print(f"{outcome}  {name}")
print(f"\n{sum(r[1]=='PASS' for r in results)}/{len(results)} tests passed")
