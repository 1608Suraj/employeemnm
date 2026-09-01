import os
import sys
import streamlit as st
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import db_manager as db

st.set_page_config(page_title="Employee Management System", layout="wide")


def init_session():
    """Initialize session state for authentication."""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "username" not in st.session_state:
        st.session_state["username"] = None
    if "role" not in st.session_state:
        st.session_state["role"] = None


def login_page():
    """Render Login and Sign Up forms."""
    st.title("Employee Management System")

    tab_login, tab_signup = st.tabs(["Login", "Sign Up"])

    with tab_login:
        st.subheader("Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")

            if submitted:
                if not username.strip() or not password:
                    st.warning("Please enter both username and password.")
                else:
                    success, message, user = db.authenticate_user(username, password)
                    if success and user:
                        st.session_state["authenticated"] = True
                        st.session_state["username"] = user["username"]
                        st.session_state["role"] = user.get("role", "admin")
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

    with tab_signup:
        st.subheader("Create Account")
        with st.form("signup_form", clear_on_submit=True):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Register")

            if submitted:
                if not new_username.strip():
                    st.warning("Username cannot be empty.")
                elif len(new_password) < 4:
                    st.warning("Password must be at least 4 characters.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    success, msg = db.create_user(new_username.strip(), new_password)
                    if success:
                        st.success(f"{msg} Please login.")
                    else:
                        st.error(msg)


def main_app():
    """Main application after login - CRUD operations."""
    st.title("Employee Management System")

    # Sidebar - user info and navigation
    st.sidebar.write(f"Logged in as: **{st.session_state['username']}** ({st.session_state['role']})")
    if st.sidebar.button("Logout"):
        st.session_state["authenticated"] = False
        st.session_state["username"] = None
        st.session_state["role"] = None
        st.rerun()

    menu = ["Add Employee", "Remove Employee", "Promote Employee", "Display Employees"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Add Employee":
        st.subheader("Add New Employee")
        with st.form("add_employee_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Name")
                position = st.text_input("Position")
            with col2:
                salary = st.number_input("Salary", min_value=0.0, format="%.2f")

            submitted = st.form_submit_button("Add Employee")
            if submitted:
                if name.strip() and position.strip():
                    success, msg, new_id = db.add_employee(name.strip(), position.strip(), salary)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
                else:
                    st.warning("Please fill in all fields.")

    elif choice == "Remove Employee":
        st.subheader("Remove Employee")
        employees = db.get_all_employees()
        if employees:
            df = pd.DataFrame(employees)
            st.dataframe(df, use_container_width=True)

            emp_id = st.number_input("Enter Employee ID to Remove", min_value=1)
            if st.button("Remove Employee"):
                success, msg = db.remove_employee(emp_id)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
        else:
            st.info("No employees found.")

    elif choice == "Promote Employee":
        st.subheader("Promote Employee")
        employees = db.get_all_employees()
        if employees:
            df = pd.DataFrame(employees)
            st.dataframe(df, use_container_width=True)

            emp_id = st.number_input("Enter Employee ID to Promote", min_value=1)
            new_position = st.text_input("New Position")
            new_salary = st.number_input("New Salary", min_value=0.0, format="%.2f")

            if st.button("Update Employee"):
                if new_position.strip() and new_salary > 0:
                    success, msg = db.promote_employee(emp_id, new_position.strip(), new_salary)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.warning("Please provide new position and salary.")
        else:
            st.info("No employees found.")

    elif choice == "Display Employees":
        st.subheader("Employee Records")
        employees = db.get_all_employees()
        if employees:
            df = pd.DataFrame(employees)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No employees found.")


def main():
    init_session()

    # Initialize DB once per session
    if "db_initialized" not in st.session_state:
        ok, msg = db.init_db()
        st.session_state["db_initialized"] = ok
        st.session_state["db_error"] = msg if not ok else None

    if not st.session_state.get("db_initialized", False):
        st.warning("⚠️ Could not connect to MySQL database. Please verify your connection or Streamlit Cloud Secrets.")
        with st.expander("ℹ️ Streamlit Cloud Secrets Setup"):
            st.markdown("""
            Add your cloud database credentials in **App Settings → Secrets**:
            ```toml
            [mysql]
            host = "your-host.aiven.io"
            port = 3306
            user = "avnadmin"
            password = "your_password"
            database = "defaultdb"
            ```
            """)

    if not st.session_state["authenticated"]:
        login_page()
    else:
        main_app()


if __name__ == '__main__':
    main()
