import sqlite3
import bcrypt
import datetime
from modules.db_service import get_connection


def hash_password(plain_password):
    return bcrypt.hashpw(
        plain_password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def register_user(name, email, password):
    """
    Registers a new user.
    Returns (True, "Success") or (False, "error message").
    """
    if not name.strip():
        return False, "Name cannot be empty."
    if not email.strip() or "@" not in email:
        return False, "Please enter a valid email address."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT id FROM users WHERE email = ?",
            (email.lower().strip(),)
        )
        if cursor.fetchone():
            return False, "An account with this email already exists."

        password_hash = hash_password(password)

        cursor.execute("""
            INSERT INTO users (name, email, password_hash, created_at)
            VALUES (?, ?, ?, ?)
        """, (
            name.strip(),
            email.lower().strip(),
            password_hash,
            datetime.date.today().strftime("%d %B %Y")
        ))

        conn.commit()
        return True, "Account created successfully."

    except Exception as e:
        return False, f"Registration error: {str(e)}"

    finally:
        conn.close()


def login_user(email, password):
    """
    Validates credentials.
    Returns (True, user_dict) or (False, "error message").
    """
    if not email.strip() or not password.strip():
        return False, "Please enter both email and password."

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT * FROM users WHERE email = ?",
            (email.lower().strip(),)
        )
        user = cursor.fetchone()

        if not user:
            return False, "No account found with this email."

        if not verify_password(password, user["password_hash"]):
            return False, "Incorrect password."

        return True, {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"]
        }

    except Exception as e:
        return False, f"Login error: {str(e)}"

    finally:
        conn.close()