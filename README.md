# Employee Management Portal (Python + Streamlit + MySQL)

A modern, secure, database-driven **Employee Management Portal** built with **Streamlit**, **MySQL**, and **bcrypt** authentication.

---

## 🚀 Key Features

- 🔐 **Authentication & Access Control**:
  - Secure Login & User Registration with **bcrypt** salted password hashing.
  - Session state persistence preventing unauthorized access.
  - Role management (Admin, Manager, Staff) with active user status badges.
- 📊 **Dashboard & Metrics Overview**:
  - Real-time KPI summary cards: Total Headcount, Total Monthly Payroll, Average Salary, Unique Positions.
  - Real-time search by Employee Name or ID, plus filtering by Job Designation.
  - Formatted currency presentation and One-Click CSV Export.
- ➕ **Add Employee**:
  - Clean form with input validation (trimmed strings, positive salary checks, informative alerts).
- 📈 **Promote / Update Employee**:
  - Interactive employee dropdown selector that automatically pre-populates existing position and salary.
  - Verified row updates with accurate database status feedback.
- 🗑️ **Remove Employee**:
  - Interactive employee selector with profile preview and safety confirmation checkbox to prevent accidental deletions.
  - Database rowcount verification preventing false-positive success messages.

---

## 📂 Project Structure

- **`app.py`**: Streamlit application with authentication gating, session management, and CRUD views.
- **`db_manager.py`**: Backend database layer handling MySQL operations, user authentication, bcrypt hashing, and verified CRUD transactions.
- **`db_config.py`**: MySQL connection credentials.
- **`requirements.txt`**: Project dependencies (`streamlit`, `mysql-connector-python`, `pandas`, `bcrypt`).
- **`test_auth_and_db.py`**: Automated test suite for authentication, role handling, and database operations.

---

## 🔑 Default Credentials

The database automatically initializes a default administrator account on first run:

| Username | Password | Role |
| :--- | :--- | :--- |
| `admin` | `admin123` | Admin |

> You can also create custom accounts using the **Create Account** tab on the login screen.

---

## ⚙️ Installation & Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Database**:
   Open `db_config.py` and verify your MySQL connection settings:
   ```python
   DB_CONFIG = {
       'host': 'localhost',
       'user': 'root',
       'password': 'your_password',
       'database': 'employee_db'
   }
   ```

3. **Initialize Database**:
   Initialize the database schema, `employees` table, `users` table, and default admin:
   ```bash
   python db_manager.py
   ```

4. **Run Automated Verification Tests (Optional)**:
   ```bash
   python test_auth_and_db.py
   ```

---

## ▶️ Execution

Launch the Streamlit web application:

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`.
