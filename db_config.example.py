import streamlit as st

# ============================================================
# SETUP: Copy this file as 'db_config.py' and fill in your
# MySQL credentials. db_config.py is gitignored for security.
# ============================================================

# Use Streamlit Secrets (cloud) if available, otherwise fallback to local config
try:
    DB_CONFIG = {
        'host': st.secrets["mysql"]["host"],
        'user': st.secrets["mysql"]["user"],
        'password': st.secrets["mysql"]["password"],
        'database': st.secrets["mysql"]["database"]
    }
except Exception:
    # Local development fallback
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'your_mysql_username',
        'password': 'your_mysql_password',
        'database': 'employee_db'
    }
