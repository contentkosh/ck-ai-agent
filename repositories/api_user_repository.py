from sqlalchemy.orm import Session
from database.model.api_user import ApiUser

def create_api_user(
    db: Session,
    username: str,
    token: str,
    role: str,
    expires_at=None,
) -> ApiUser:
    """
    Create and store a new API user.
    """
    api_user = ApiUser(
        username=username,
        token=token,
        role=role,
        expires_at=expires_at,
    )

    db.add(api_user)
    db.commit()
    db.refresh(api_user)

    return api_user

def get_api_user_by_token(
    db: Session,
    token: str,
) -> ApiUser | None:
    """
    Retrieve an API user using its authentication token.
    """
    return (
        db.query(ApiUser)
        .filter(ApiUser.token == token)
        .first()
    )