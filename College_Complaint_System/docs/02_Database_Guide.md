# Guide 2: Understanding the Database

This guide explains **where and how every complaint is remembered**. Written for a complete beginner.

---

## 1. What is a database?

A database is **an organised notebook that a computer can read very fast**.

> **Real-world example:** Think of your school's attendance register. It has columns (Roll No, Name, Date, Present/Absent) and many rows, one per student. Anyone can open it and find a student quickly. A database is the same thing, except the computer keeps it, and it can hold millions of rows.

If we did not have a database, the complaints would vanish the moment you closed the program, like writing on a whiteboard and then someone wiping it clean. The database is like writing in a **pen on paper**: it stays.

---

## 2. What is SQLite?

There are many database programs (MySQL, Oracle, and so on). Most need a separate big program running, like a whole office with staff.

**SQLite is the pocket-sized version.** The whole database is **one single file** on your computer. No setup, no passwords, no installation. Python already knows how to talk to it.

In our project that file is:
```
College_Complaint_System/data/complaints.db
```
You can copy it, email it, or delete it like any other file.

> **Real-world example:** A big bank keeps records in a huge building. SQLite is like a single diary in your bag. For a college project, a diary is perfect.

---

## 3. How many tables do we have?

**Just one table**, called `complaints`.

A **table** is one sheet in the register, with a fixed set of columns. Our project is small, so one sheet is enough.

> We keep it at one table on purpose, because the brief says "simple prototype". Later, if you add a *Users* table or a *Categories* table, you would add more sheets to the register.

---

## 4. The `complaints` table: column by column

Each **row** is one complaint (one paper slip). Each **column** is one piece of information written on every slip.

| Column | Type | What it stores | Example |
| --- | --- | --- | --- |
| `id` | Number (INTEGER) | The unique Complaint ID. Counts up by itself: 1, 2, 3... | `1` |
| `submitted_by` | Text | Name or ID of the person who complained | `Asha` |
| `category` | Text | What kind of problem it is | `Electrical` |
| `description` | Text | The problem in the person's own words | `Fan not working in Room 101` |
| `submit_date` | Text | The day the complaint was submitted (YYYY-MM-DD) | `2026-11-22` |
| `status` | Text | Where the complaint is now | `Pending` |

### What the table looks like with data

| id | submitted_by | category | description | submit_date | status |
| --- | --- | --- | --- | --- | --- |
| 1 | Asha | Electrical | Fan not working in Room 101 | 2026-11-22 | In Progress |
| 2 | Ravi | Plumbing | Tap leaking in washroom | 2026-11-22 | Pending |
| 3 | Meena | Furniture | Broken bench in Class 3B | 2026-11-23 | Resolved |

### Why these columns? Matching the brief

The brief asked us to store 5 things: **ID, Category, Description, Submission date, Status.** All five are here.

We added **one extra**: `submitted_by`. Why? Imagine 100 slips in the box. When Asha asks "where is *my* complaint?", we need to know which slips are hers. Without a name on the slip, everyone would see everyone's complaints.

---

## 5. Special words in the table definition

Here is the actual instruction that builds the table (found in `src/database.py`):

```sql
CREATE TABLE IF NOT EXISTS complaints (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    submitted_by  TEXT NOT NULL,
    category      TEXT NOT NULL,
    description   TEXT NOT NULL,
    submit_date   TEXT NOT NULL,
    status        TEXT NOT NULL DEFAULT 'Pending'
)
```

Line by line, in plain words:

| Words | Meaning | Real-world example |
| --- | --- | --- |
| `CREATE TABLE` | "Make a new sheet" | Buying a new register |
| `IF NOT EXISTS` | "Only if it is not already there" | If you already have the register, do not buy another one. This is why restarting the app never erases data. |
| `INTEGER` | A whole number | 1, 2, 3 |
| `TEXT` | Letters/words | "Fan broken" |
| `PRIMARY KEY` | The one value that is **unique** for each row, used to point at exactly one complaint | Your roll number. Two students may have the same name, but never the same roll number. |
| `AUTOINCREMENT` | The computer numbers rows for us: 1, 2, 3... never repeating | A token machine at a bank counter that hands out the next number |
| `NOT NULL` | This box **cannot be left empty** | A form where the "Name" field is mandatory |
| `DEFAULT 'Pending'` | If nobody says otherwise, write "Pending" | Every new slip starts in the "Waiting" pile |

---

## 6. The life of a complaint (status)

There are only **three allowed statuses**:

```
   Pending  ──►  In Progress  ──►  Resolved
   (waiting)     (being fixed)     (fixed!)
```

- A new complaint is **always Pending**. The student cannot choose anything else.
- Only the **Administrator** changes the status.

> **Real-world example, a pizza order:** *Order received* (Pending) → *In the oven* (In Progress) → *Delivered* (Resolved).

The program refuses any other word, like "Done" or "Okay". This is a **rule that protects the data**, the way a vending machine refuses coins it does not know.

---

## 7. The four basic actions (CRUD)

Every database program does just four things. Remember the word **CRUD**:

| Letter | Action | In our project | SQL word |
| --- | --- | --- | --- |
| **C** | Create | A student submits a complaint | `INSERT` |
| **R** | Read | View my complaints / admin views all | `SELECT` |
| **U** | Update | Admin changes the status | `UPDATE` |
| **D** | Delete | (not needed in this project) | `DELETE` |

### Example of each (these are real instructions from our code)

**Create** (a new slip goes into the box):
```sql
INSERT INTO complaints (submitted_by, category, description, submit_date, status)
VALUES ('Asha', 'Electrical', 'Fan not working', '2026-11-22', 'Pending')
```
"Add a new row with these values."

**Read** (show Asha's slips only):
```sql
SELECT id, category, description, submit_date, status
FROM complaints
WHERE LOWER(submitted_by) = LOWER('Asha')
ORDER BY id DESC
```
- `SELECT ... FROM` = "show me these columns from the table"
- `WHERE` = "only rows that match this condition" (a filter)
- `LOWER(...)` = ignore capital letters, so "asha" and "Asha" match
- `ORDER BY id DESC` = newest first (highest number on top)

**Update** (the office person writes "In Progress" on slip number 1):
```sql
UPDATE complaints SET status = 'In Progress' WHERE id = 1
```
The `WHERE id = 1` is very important. **Without it, every complaint's status would change!** It's like telling someone "mark everyone present" instead of "mark Asha present".

---

## 8. The question mark `?` (a safety rule)

In our code you will see `?` inside SQL, like this:
```python
conn.execute("UPDATE complaints SET status = ? WHERE id = ?", (new_status, complaint_id))
```

The `?` are **empty boxes** that Python fills in safely.

> **Real-world example:** A form with blanks: "My name is ______." A person can only write a name in the blank. They cannot cross out the printed form and write new rules. If we glued user text directly into the SQL, a naughty user could type tricky commands that damage the database (this is called *SQL injection*). Using `?` closes that door.

---

## 9. Where is the code that talks to the database?

Everything is in **one file**: `src/database.py`. No other file touches the database directly. 

> **Real-world example:** In a library, only the librarian goes to the shelves. Students ask the librarian, who fetches the book. In our project, `app.py` (the screens) asks, and `database.py` (the librarian) fetches. See Guide 3 for each function.

---

## 10. How to look inside the database yourself

### Option A: Use Python (no extra tools)
In the terminal, inside `College_Complaint_System`:
```
python -c "import sqlite3; print(sqlite3.connect('data/complaints.db').execute('SELECT * FROM complaints').fetchall())"
```
You will see all rows printed as a list.

### Option B: VS Code extension (nice tables)
1. In VS Code open the **Extensions** panel (square icon on the left).
2. Search for **SQLite Viewer** and install it.
3. Click on `data/complaints.db` in the file list. The table appears like a spreadsheet.

---

## 11. Putting it all together: one complaint's journey

1. **Asha** opens the page, writes "Fan not working in Room 101", clicks Submit.
2. `app.py` checks the boxes are not empty, then calls `add_complaint(...)` in `database.py`.
3. `database.py` writes a new row: `id=1`, `status=Pending`, `submit_date=today`.
4. The **Admin** opens the page. `get_all_complaints()` reads every row and shows them.
5. The Admin picks ID 1 and selects **In Progress**. `update_status(1, "In Progress")` changes only that row.
6. **Asha** opens *My Complaints*. `get_complaints_by_user("Asha")` reads her rows and she sees **In Progress**.

---

## 12. Safety and good habits

- **Use sample data only.** No real student names, phone numbers or secrets (as the brief says).
- **Back up** by copying `complaints.db` somewhere safe, like photocopying the register.
- **Do not edit the file with Notepad.** It is not a text file; you would break it.
- If it ever breaks, delete `data/complaints.db`; a fresh one is made when you restart.

Next: read **Guide 3 (Code Explanation)**.
