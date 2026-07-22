from modules.supabase_client import supabase
from postgrest.exceptions import APIError

def register_user(name, email, password):
    """
    Registers a new user using Supabase Auth.
    Returns (True, "Success") or (False, "error message").
    """

    if not name.strip():
        return False, "Name cannot be empty."

    if not email.strip() or "@" not in email:
        return False, "Please enter a valid email address."

    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    try:
        # Create auth user
        auth_response = supabase.auth.sign_up({
            "email": email.lower().strip(),
            "password": password
        })

        user = auth_response.user

        if user is None:
            return False, "Failed to create account."

        # Create profile
        supabase.table("profiles").insert({
            "id": user.id,
            "name": name.strip()
        }).execute()

        return True, "Account created successfully."

    except APIError as e:
        message = str(e)

        if "already registered" in message.lower():
            return False, "An account with this email already exists."

        return False, message

    except Exception as e:
        return False, str(e)

def login_user(email, password):
    """
    Authenticates a user using Supabase Auth.
    Returns (True, user_dict) or (False, "error message").
    """

    if not email.strip() or not password.strip():
        return False, "Please enter both email and password."

    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": email.lower().strip(),
            "password": password
        })

        user = auth_response.user

        if user is None:
            return False, "Invalid email or password."

        # Fetch profile
        profile = (
            supabase
            .table("profiles")
            .select("name")
            .eq("id", user.id)
            .single()
            .execute()
        )

        profile_data = profile.data or {}

        return True, {
            "id": user.id,
            "name": profile_data.get("name", ""),
            "email": user.email
        }

    except APIError as e:
        return False, str(e)

    except Exception as e:
        return False, str(e)