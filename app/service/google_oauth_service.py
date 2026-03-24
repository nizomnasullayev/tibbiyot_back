from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

try:
    from google.auth.transport import requests
    from google.oauth2 import id_token
    GOOGLE_AUTH_INSTALLED = True
except ImportError:
    requests = None
    id_token = None
    GOOGLE_AUTH_INSTALLED = False

# You'll get this from Google Cloud Console
# Store it in your settings/environment variables
GOOGLE_CLIENT_ID = None  # Will be set from config

    
def set_google_client_id(client_id: str):
    """Set the Google Client ID (call this during app startup)"""
    global GOOGLE_CLIENT_ID
    GOOGLE_CLIENT_ID = client_id
    print(f"Google Client ID set: {client_id[:30]}...")


def verify_google_token(token: str) -> dict:
    """
    Verify Google ID token and return user info.

    Args:
        token: Google ID token from frontend

    Returns:
        User info: {email, name, picture, sub (Google ID)}

    Raises:
        HTTPException: If token is invalid
    """
    print("\n" + "=" * 60)
    print("🔐 Google Token Verification Started")
    print("=" * 60)

    # Debug: Check if Client ID is set
    if not GOOGLE_AUTH_INSTALLED:
        raise HTTPException(
            status_code=503,
            detail="Google authentication requires google-auth to be installed",
        )

    if not GOOGLE_CLIENT_ID:
        logger.error("Google Client ID not configured")
        print("❌ GOOGLE_CLIENT_ID is None!")
        raise HTTPException(
            status_code=500,
            detail="Google authentication not configured"
        )

    print(f"✅ GOOGLE_CLIENT_ID: {GOOGLE_CLIENT_ID[:30]}...")
    print(f"✅ Token received (length: {len(token)} chars)")
    print(f"   Token preview: {token[:50]}...")

    try:
        # Verify the token
        print("\n🔍 Verifying with Google servers...")
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )

        print("✅ Token verified successfully!")
        print(f"   Email: {idinfo.get('email')}")
        print(f"   Name: {idinfo.get('name')}")
        print(f"   Issuer: {idinfo.get('iss')}")

        # Verify it's from Google
        issuer = idinfo.get("iss")
        if issuer not in ["accounts.google.com", "https://accounts.google.com"]:
            print(f"❌ Invalid issuer: {issuer}")
            raise ValueError(f"Invalid token issuer: {issuer}")

        print("✅ Issuer verified!")

        # Token is valid, return user info
        user_info = {
            "email": idinfo.get("email"),
            "name": idinfo.get("name"),
            "picture": idinfo.get("picture"),
            "sub": idinfo.get("sub"),  # Google user ID
            "verified_email": idinfo.get("email_verified", False),
        }

        print(f"✅ User info extracted: {user_info}")
        print("=" * 60 + "\n")
        return user_info

    except ValueError as e:
        print(f"❌ ValueError: {e}")
        logger.error(f"Invalid Google token: {e}")
        raise HTTPException(
            status_code=401,
            detail=f"Invalid Google token: {str(e)}"
        )
    except Exception as e:
        print(f"❌ Exception: {type(e).__name__}: {e}")
        logger.error(f"Error verifying Google token: {e}")
        raise HTTPException(
            status_code=401,
            detail=f"Failed to verify Google token: {str(e)}"
        )
