"""app.py - the Streamlit screens. Run with:  streamlit run app.py"""
import pandas as pd
import streamlit as st

import database as db

ADMIN_PASSWORD = "admin123"  # prototype only - a real system would not hard-code this

COLUMNS_USER = ["ID", "Category", "Description", "Date", "Status"]
COLUMNS_ADMIN = ["ID", "Submitted By", "Category", "Description", "Date", "Status"]

db.create_table()  # make sure the table exists

st.set_page_config(page_title="College Complaint System", page_icon="🛠️")
st.title("🛠️ College Complaint & Maintenance System")

role = st.sidebar.radio("I am a...", ["Student / Staff", "Administrator"])


# ---------------- Student / Staff ----------------
def student_screen():
    name = st.sidebar.text_input("Your name or ID", help="Used to find your complaints later.")
    tab1, tab2 = st.tabs(["Register Complaint", "My Complaints"])

    with tab1:
        with st.form("complaint_form", clear_on_submit=True):
            category = st.selectbox("Category", db.CATEGORIES)
            description = st.text_area("Describe the problem")
            submitted = st.form_submit_button("Submit Complaint")
        if submitted:
            if not name.strip():
                st.error("Please enter your name or ID in the sidebar first.")
            elif not description.strip():
                st.error("Please describe the problem.")
            else:
                new_id = db.add_complaint(name, category, description)
                st.success(f"Complaint registered! Your Complaint ID is {new_id} (status: Pending).")

    with tab2:
        if not name.strip():
            st.info("Enter your name or ID in the sidebar to see your complaints.")
        else:
            rows = db.get_complaints_by_user(name)
            if rows:
                st.dataframe(pd.DataFrame(rows, columns=COLUMNS_USER), hide_index=True)
            else:
                st.write("No complaints found for this name.")


# ---------------- Administrator ----------------
def admin_screen():
    password = st.sidebar.text_input("Admin password", type="password")
    if password != ADMIN_PASSWORD:
        st.info("Enter the admin password in the sidebar.")
        return

    st.subheader("Update a complaint's status")
    all_ids = [r[0] for r in db.get_all_complaints()]
    if all_ids:
        with st.form("status_form"):
            cid = st.selectbox("Complaint ID", all_ids)
            new_status = st.selectbox("New status", db.STATUSES)
            go = st.form_submit_button("Update Status")
        if go:
            db.update_status(cid, new_status)
            st.success(f"Complaint {cid} is now '{new_status}'.")

    st.subheader("All complaints")
    choice = st.selectbox("Filter by status", ["All"] + db.STATUSES)
    rows = db.get_all_complaints(None if choice == "All" else choice)
    if rows:
        st.dataframe(pd.DataFrame(rows, columns=COLUMNS_ADMIN), hide_index=True)
    else:
        st.write("No complaints to show.")


if role == "Student / Staff":
    student_screen()
else:
    admin_screen()
