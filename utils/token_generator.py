import secrets

def generate_api_token() -> str:
    """
    Generate a secure random token for an API user.
    """
    return secrets.token_urlsafe(32)