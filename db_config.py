import streamlit as st

# Use Streamlit Secrets (cloud) if available, otherwise fallback to local config
try:
    DB_CONFIG = {
        'host': st.secrets["mysql"]["host"],
        'port': int(st.secrets["mysql"].get("port", 3306)),
        'user': st.secrets["mysql"]["user"],
        'password': st.secrets["mysql"]["password"],
        'database': st.secrets["mysql"]["database"]
    }
except Exception:
    # Local development fallback
    DB_CONFIG = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': 'root',
        'database': 'employee_db'
    }
