# Guide 3: Understanding the Code, File by File

This guide explains **what every file does and why it exists**, using everyday examples. You do not need to know programming already.

---

## 1. The map: what is in each folder?

```
College_Complaint_System/
│
├── src/                    <- "source": the real program
│   ├── app.py              <- the screens people see (front desk)
│   └── database.py         <- the storage worker (librarian)
│
├── tests/
│   └── test_database.py    <- automatic checker (examiner)
│
├── data/
│   └── complaints.db       <- the saved complaints (made automatically)
│
├── docs/                   <- guides like this one
├── requirements.txt        <- shopping list of extra tools
├── README.md               <- front page of the project
└── .gitignore              <- list of files Git should not save
```

> **Real-world example: a restaurant.**
> - `app.py` = the **waiter**. Talks to customers, takes orders, shows the menu.
> - `database.py` = the **kitchen/storeroom**. Keeps the ingredients (data) and prepares what is asked.
> - `complaints.db` = the **fridge**. The actual stuff that is stored.
> - `test_database.py` = the **food inspector** who checks the kitchen works properly.

The waiter never goes into the fridge himself. He always asks the kitchen. In our code, `app.py` never touches the database directly. It always asks `database.py`. This keeps everything tidy: if you want to change how data is saved, you only change one file.

---

## 2. How the pieces talk to each other

```
 Person in browser
        │  clicks, types
        ▼
 ┌──────────────┐   "please add this complaint"   ┌───────────────┐   writes   ┌──────────────┐
 │   app.py     │ ──────────────────────────────► │  database.py  │ ─────────► │ complaints.db│
 │ (screens)    │ ◄────────────────────────────── │  (storage)    │ ◄───────── │  (the file)  │
 └──────────────┘   "done, ID is 5" / the list    └───────────────┘   reads    └──────────────┘
```

---

## 3. A few Python words you will meet

| Word | Simple meaning | Real-world example |
| --- | --- | --- |
| `import` | Borrow a ready-made toolbox | Borrowing a calculator instead of building one |
| **variable** (`name = "Asha"`) | A labelled box holding a value | A lunch box with a name sticker |
| **function** (`def add_complaint(...)`) | A named recipe you can use again and again | A recipe card: "how to make tea" |
| **parameter** | Ingredients you hand to the recipe | The recipe needs "water, tea leaves, sugar" |
| `return` | The recipe hands you back a result | The cup of tea |
| **list** (`["a", "b"]`) | Items in a row | A shopping list |
| `if / elif / else` | Make a decision | "If it rains, take an umbrella" |
| `with` | Open something, use it, close it safely | Opening a door, walking through, closing it behind you |
| `#` comment | A note for humans; the computer ignores it | A sticky note on a page |
| `"""text"""` | A longer note describing a function | The label on a medicine bottle |

---

## 4. File: `src/database.py` (the storage worker)

This file contains the only code that talks to SQLite. Read it from top to bottom.

### 4.1 The top of the file: settings

```python
import os
import sqlite3
from datetime import date

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(PROJECT_DIR, "data", "complaints.db")
STATUSES = ["Pending", "In Progress", "Resolved"]
CATEGORIES = ["Electrical", "Plumbing", "Furniture", "Computer Lab", "Fans / Lights", "Other"]
```

- `import sqlite3` borrows Python's database toolbox.
- `import os` helps work with file locations.
- `from datetime import date` borrows the calendar, so we can ask for today's date.
- `PROJECT_DIR` works out **where the project folder is** (from where this file lives), so the program works no matter where you start it from. Real-world: giving directions *from the house*, not from "wherever you are standing".
- `DB_FILE` is the address of the database: `data/complaints.db`.
- `STATUSES` is the **list of allowed statuses**. Only these three exist.
- `CATEGORIES` is the **list of complaint types** shown in the drop-down. To add a category, add a word here (for example `"Hostel"`). Nothing else needs changing.

### 4.2 `get_connection()`: opening the notebook

```python
def get_connection(db_file=DB_FILE):
    os.makedirs(os.path.dirname(os.path.abspath(db_file)), exist_ok=True)
    return sqlite3.connect(db_file)
```
- Makes sure the `data` folder exists (creates it if missing).
- Opens the database file. If it does not exist yet, SQLite **creates it**.

> Real-world example: walking up to the cupboard and opening the door. A "connection" is just an open door to the database.

### 4.3 `create_table()`: preparing the register

Runs `CREATE TABLE IF NOT EXISTS complaints (...)` (explained in Guide 2). It is called every time the app starts, but only builds the table **if it is missing**. So your data is never erased by restarting.

### 4.4 `add_complaint()`: registering a complaint (**Create**)

```python
def add_complaint(submitted_by, category, description, db_file=DB_FILE):
    submitted_by, description = submitted_by.strip(), description.strip()
    if not submitted_by or not description:
        raise ValueError("Name and description cannot be empty.")
    with get_connection(db_file) as conn:
        cur = conn.execute("INSERT INTO complaints (...) VALUES (?, ?, ?, ?, 'Pending')", (...))
        return cur.lastrowid
```
Step by step:
1. `.strip()` removes extra spaces at the start/end. (`"  hello "` becomes `"hello"`.)
2. If the name or description is empty, it **stops and complains** with an error (`ValueError`). This is a safety check, like a gatekeeper refusing a blank form.
3. Opens the database and inserts a new row.
4. The status is written as **Pending** by the code itself. The user cannot choose.
5. The date is `date.today().isoformat()`, which gives `2026-11-22` style text.
6. Returns `cur.lastrowid`, meaning **the ID the computer just gave this complaint**, like the token number you get at a bank.

### 4.5 `get_complaints_by_user()`: "show me my complaints" (**Read**)

Selects only the rows where the name matches (ignoring capitals), newest first. Returns a list of rows, each row being `(id, category, description, date, status)`.

> Real-world example: asking the librarian "show me all books borrowed by Asha".

### 4.6 `get_all_complaints()`: the admin's view (**Read**)

Returns **every** complaint with the person's name too. If you give it a status (like `"Pending"`), it returns only those. This powers the filter on the admin page.

> Real-world example: the principal asking, "Show me every complaint" or "Show me only the ones still waiting".

### 4.7 `update_status()`: change the status (**Update**)

```python
def update_status(complaint_id, new_status, db_file=DB_FILE):
    if new_status not in STATUSES:
        raise ValueError(...)
    ...UPDATE complaints SET status = ? WHERE id = ?...
    return cur.rowcount == 1
```
1. Checks the new status is one of the three allowed words. If not, error.
2. Updates only the complaint with that ID.
3. Returns `True` if exactly one row changed, `False` if that ID did not exist.

### A note on `db_file=DB_FILE`

Every function accepts an optional `db_file`. Normally you do not pass it, so the real database is used. The **tests** pass a temporary file, so testing never damages real data. 

> Real-world example: a driving test car with a second set of pedals. Same car, but safe for practice.

---

## 5. File: `src/app.py` (the screens)

This is the file Streamlit runs. Streamlit reads it **from top to bottom every time you click something**. Think of it as redrawing the page from scratch after every click.

### 5.1 The top: borrowing and settings

```python
import pandas as pd
import streamlit as st
import database as db

ADMIN_PASSWORD = "admin123"
COLUMNS_USER = ["ID", "Category", "Description", "Date", "Status"]
COLUMNS_ADMIN = ["ID", "Submitted By", "Category", "Description", "Date", "Status"]
```
- `streamlit as st` gives us short-hand `st` for drawing things (buttons, boxes).
- `pandas as pd` turns rows into a neat table with column headings. (It was installed together with Streamlit.)
- `import database as db` borrows **our own** `database.py`. Now `db.add_complaint(...)` means "ask the storage worker to add a complaint".
- `ADMIN_PASSWORD` is the password. It is written in the code only because this is a learning prototype. A real system would never do that.
- `COLUMNS_...` are the column titles for the tables on screen.

### 5.2 Starting up

```python
db.create_table()
st.set_page_config(page_title="College Complaint System", page_icon="🛠️")
st.title("🛠️ College Complaint & Maintenance System")
role = st.sidebar.radio("I am a...", ["Student / Staff", "Administrator"])
```
1. Make sure the table exists.
2. Set the browser tab title.
3. Show the big heading.
4. Draw the **role selector** (two round buttons in the left sidebar). The choice is stored in `role`.

### 5.3 `student_screen()`: what a student sees

- A text box in the sidebar for **name or ID**.
- `st.tabs([...])` creates two tabs.
- **Tab 1, "Register Complaint"**: a `st.form` holding a **category drop-down**, a **description box** and a **Submit button**. 
  - A *form* means the page waits until you click Submit before doing anything. (Without it, the page would react to every single key you type.)
  - `clear_on_submit=True` empties the boxes after submitting, like a fresh blank slip.
  - When Submit is clicked, the code checks: name empty? show a red error. Description empty? red error. Otherwise call `db.add_complaint(...)` and show a green success message with the new ID.
- **Tab 2, "My Complaints"**: if no name yet, show a blue hint. Otherwise call `db.get_complaints_by_user(name)` and show the rows as a table.

### 5.4 `admin_screen()`: what the administrator sees

1. Asks for the password in the sidebar. If it is wrong, shows a hint and **stops** (`return`), so nothing else is shown.
2. **"Update a complaint's status"** form: pick an ID, pick a new status, click **Update Status**, which calls `db.update_status(...)`.
3. **"All complaints"**: a status filter and a table from `db.get_all_complaints(...)`.

The update form is placed *above* the table so that after you update, the table below already shows the new status.

### 5.5 The last lines: pick the screen

```python
if role == "Student / Staff":
    student_screen()
else:
    admin_screen()
```
> Like a receptionist: "Are you a student? Go to Room A. Otherwise go to Room B."

---

## 6. File: `tests/test_database.py` (the examiner)

This script **tests the storage worker automatically**.

How it works:
1. It makes a **temporary** database in a throwaway folder.
2. It tries 11 things, such as adding a complaint, checking it starts as Pending, updating status, and trying bad input.
3. For each one, `check("name", condition)` records `PASS` or `FAIL`.
4. At the end, it prints all results and a score like `11/11 tests passed`.

| Test | What it proves |
| --- | --- |
| T1 | Adding a complaint gives back an ID |
| T2 | A new complaint is Pending |
| T3 | A user sees only their own complaints (and capitals do not matter) |
| T4 | The admin sees all complaints |
| T5, T6 | Status can change to In Progress, then Resolved |
| T7 | The user sees the updated status |
| T8 | Filtering by status works |
| T9 | A wrong status like "Done" is rejected |
| T10 | An empty description is rejected |
| T11 | Updating a non-existent ID changes nothing |

The first lines of the file tell Python where to find `src/database.py` (`sys.path.insert(...)`), since the tests live in a different folder.

> Real-world example: a quality check on a factory line. Every product (function) is tested before it leaves.

**Adding your own test:** copy one of the `check(...)` lines, change the name and condition, and run the file again. Keep the output for your report.

---

## 7. Other files

| File | Purpose |
| --- | --- |
| `requirements.txt` | A shopping list of extra tools (`streamlit`). Someone else can run `pip install -r requirements.txt` to get everything. |
| `.gitignore` | Tells Git not to upload `data/*.db` (your personal data) or `__pycache__` (computer-made temporary files). |
| `README.md` | The front page, with the folder map and the start command. |
| `data/complaints.db` | The SQLite database. Created automatically. |

---

## 8. Following one click through the code

**Asha clicks "Submit Complaint":**
1. Streamlit re-reads `app.py` from top to bottom.
2. `student_screen()` runs and sees `submitted` is `True`.
3. Name and description are not empty, so it calls `db.add_complaint("Asha", "Electrical", "Fan not working in Room 101")`.
4. In `database.py`: trims spaces, checks not empty, opens `complaints.db`, runs `INSERT`, gets ID `1`.
5. Back in `app.py`: shows "Complaint registered! Your Complaint ID is 1 (status: Pending)."

---

## 9. Easy changes to practise with

| I want to... | Change this |
| --- | --- |
| Add a new category (e.g. "Hostel") | `CATEGORIES` list in `src/database.py` |
| Change the admin password | `ADMIN_PASSWORD` in `src/app.py` |
| Change the page title | `st.title(...)` in `src/app.py` |
| Rename a column heading on screen | `COLUMNS_USER` / `COLUMNS_ADMIN` in `src/app.py` |

After saving a change, the browser shows a **"Source file changed → Rerun"** message. Click **Rerun** (or "Always rerun") to see the update.

---

## 10. Words to remember (mini dictionary)

| Word | Meaning |
| --- | --- |
| **Table** | One sheet in the register |
| **Row** | One complaint |
| **Column** | One kind of information (like Status) |
| **Primary key** | The unique number for each row |
| **Function** | A reusable recipe |
| **Import** | Borrow a toolbox |
| **Form** | Screen section that waits for the Submit button |
| **Sidebar** | The panel on the left of the page |
| **Test** | A small program that checks another program |
