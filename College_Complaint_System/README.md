# College Complaint & Maintenance Management System

Beginner-friendly prototype using Python, Streamlit and SQLite.

## Files
| File | What it does |
| --- | --- |
| `database.py` | All SQLite code: create table, add, view, update complaints |
| `app.py` | Streamlit screens (Student/Staff and Administrator) |
| `test_database.py` | 11 simple tests; run and keep the output as testing evidence |
| `complaints.db` | Created automatically on first run |

## Run
```
cd College_Complaint_System
streamlit run app.py
python test_database.py
```

## Using it
- **Student/Staff:** type your name/ID in the sidebar, submit a complaint (starts as Pending), and check "My Complaints" for status.
- **Administrator:** choose Administrator, password `admin123` (prototype only), view/filter all complaints, update status.

Note: a "Submitted By" column was added to the 5 required fields so each user can see only their own complaints. Use sample data only.
