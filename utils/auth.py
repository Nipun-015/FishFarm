import requests

# Firebase Configuration
FIREBASE_WEB_API_KEY = "AIzaSyCbPmgInOmGSXtGiOjkfwQXl_4GfU14nVY"
FIREBASE_SIGN_IN_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"

# Admin credentials
ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "adminpassword123"

def login_user(email, password):
    """
    Authenticates a user using Firebase REST API.
    Determines if the user is an admin or customer.
    """
    try:
        # Authenticate with Firebase REST API
        response = requests.post(
            FIREBASE_SIGN_IN_URL,
            json={
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
        )
        response_data = response.json()

        if response.status_code == 200:
            # Authentication successful
            if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
                return "admin", True  # Admin role
            else:
                return "customer", True  # Customer role
        else:
            # Handle authentication errors
            error_message = response_data.get("error", {}).get("message", "Unknown error")
            print(f"Login failed: {error_message}")
            return None, False

    except Exception as e:
        print(f"Login error: {e}")
        return None, False
