from datetime import datetime
from sqlalchemy.orm import Session
from database.model.api_user import ApiUser
from repositories.api_user_repository import (
    create_api_user,
    get_api_user_by_token,
)

def create_api_user_service(
    db: Session,
    username: str,
    token: str,
    role: str,
    expires_at=None,
) -> ApiUser:
    """
    Create an API user.
    """
    return create_api_user(
        db=db,
        username=username,
        token=token,
        role=role,
        expires_at=expires_at,
    )

def validate_api_user_token(
    db: Session,
    token: str,
) -> ApiUser | None:
    """
    Retrieve and validate an API user using its token.
    """
    api_user = get_api_user_by_token(
        db=db,
        token=token,
    )

    if api_user is None:
        return None

    if not api_user.is_active:
        return None

    if (
        api_user.expires_at is not None
        and api_user.expires_at <= datetime.utcnow()
    ):
        return None

    return api_user