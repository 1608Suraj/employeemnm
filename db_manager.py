import os
import sys
import mysql.connector
from mysql.connector import Error
import bcrypt
import streamlit as st

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def get_db_config():
    """Retrieve DB credentials from Streamlit secrets, environment, or localhost defaults."""
    try:
        if hasattr(st, "secrets") and "mysql" in st.secrets:
            return {
                'host': st.secrets["mysql"]["host"],
                'port': int(st.secrets["mysql"].get("port", 3306)),
                'user': st.secrets["mysql"]["user"],
                'password': str(st.secrets["mysql"]["password"]),
                'database': st.secrets["mysql"]["database"]
            }
    except Exception:
        pass

    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', 'root'),
        'database': os.getenv('DB_NAME', 'employee_db')
    }


def hash_password(password):
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')


def verify_password(password, hashed_password):
    """Verify a password against its bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False


def get_db_connection():
    """Connect to the MySQL database with a 5-second timeout."""
    config = get_db_config()
    try:
        connection = mysql.connector.connect(
            host=config['host'],
            port=config.get('port', 3306),
            user=config['user'],
            password=config['password'],
            database=config['database'],
            connect_timeout=5
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to database: {e}")
    return None


def init_db():
    """Initialize database tables and seed default admin user."""
    config = get_db_config()

    # If local database doesn't exist yet, try to create it
    try:
        conn_server = mysql.connector.connect(
            host=config['host'],
            port=config.get('port', 3306),
            user=config['user'],
            password=config['password'],
            connect_timeout=5
        )
        if conn_server and conn_server.is_connected():
            cursor = conn_server.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{config['database']}`")
            cursor.close()
            conn_server.close()
    except Exception:
        pass  # On cloud MySQL, DB already exists or user has restricted permissions

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    position VARCHAR(100) NOT NULL,
                    salary DECIMAL(10, 2) NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    role VARCHAR(20) NOT NULL DEFAULT 'admin',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

            # Seed default admin if not exists
            cursor.execute("SELECT id FROM users WHERE username = 'admin'")
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                    ("admin", hash_password("admin123"), "admin")
                )
                conn.commit()

            return True, "Database initialized."
        except Error as e:
            print(f"Error initializing database tables: {e}")
            return False, str(e)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    return False, "Failed to connect to MySQL database."


# ==================== Authentication ====================

def create_user(username, password, role="admin"):
    """Register a new user."""
    username = username.strip()
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(password) < 4:
        return False, "Password must be at least 4 characters."

    conn = get_db_connection()
    if not conn:
        return False, "Database connection failed. Please check MySQL settings."

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            return False, f"Username '{username}' already exists."

        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
            (username, hash_password(password), role)
        )
        conn.commit()
        return True, f"User '{username}' registered successfully!"
    except Error as e:
        return False, f"Error: {e}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


def authenticate_user(username, password):
    """Authenticate user credentials."""
    username = username.strip()
    if not username or not password:
        return False, "Please provide both username and password.", None

    conn = get_db_connection()
    if not conn:
        return False, "Database connection failed. Please check MySQL server.", None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, username, password_hash, role FROM users WHERE username = %s",
            (username,)
        )
        user = cursor.fetchone()

        if not user:
            return False, "Invalid username or password.", None

        if verify_password(password, user["password_hash"]):
            user.pop("password_hash")
            return True, f"Welcome back, {username}!", user
        else:
            return False, "Invalid username or password.", None
    except Error as e:
        return False, f"Error: {e}", None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


# ==================== Employee CRUD ====================

def add_employee(name, position, salary):
    """Add employee."""
    conn = get_db_connection()
    if not conn:
        return False, "Database connection failed.", None

    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO employees (name, position, salary) VALUES (%s, %s, %s)",
            (name, position, salary)
        )
        conn.commit()
        return True, f"Employee '{name}' added successfully!", cursor.lastrowid
    except Error as e:
        return False, f"Error adding employee: {e}", None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


def remove_employee(emp_id):
    """Remove employee by ID."""
    conn = get_db_connection()
    if not conn:
        return False, "Database connection failed."

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM employees WHERE id = %s", (emp_id,))
        conn.commit()
        if cursor.rowcount > 0:
            return True, f"Employee #{emp_id} removed successfully."
        else:
            return False, f"No employee found with ID #{emp_id}."
    except Error as e:
        return False, f"Error: {e}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


def promote_employee(emp_id, new_position, new_salary):
    """Update employee position and salary."""
    conn = get_db_connection()
    if not conn:
        return False, "Database connection failed."

    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE employees SET position = %s, salary = %s WHERE id = %s",
            (new_position, new_salary, emp_id)
        )
        conn.commit()
        if cursor.rowcount > 0:
            return True, f"Employee #{emp_id} promoted successfully!"
        else:
            return False, f"No employee found with ID #{emp_id}."
    except Error as e:
        return False, f"Error: {e}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


def get_employee_by_id(emp_id):
    """Fetch a single employee by ID."""
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM employees WHERE id = %s", (emp_id,))
        return cursor.fetchone()
    except Error as e:
        print(f"Error: {e}")
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


def get_all_employees():
    """Fetch all employee records."""
    conn = get_db_connection()
    employees = []
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM employees ORDER BY id ASC")
            employees = cursor.fetchall()
        except Error as e:
            print(f"Error fetching employees: {e}")
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
    return employees


if __name__ == '__main__':
    init_db()
