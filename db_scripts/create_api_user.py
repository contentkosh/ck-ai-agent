from database.postgres_client import SessionLocal
from services.api_user_service import create_api_user_service
from utils.token_generator import generate_api_token

def main() -> None:
    username = input("Enter username: ").strip()
    role = input("Enter role (ADMIN/USER/VIEWER): ").strip().upper()

    token = generate_api_token()

    db = SessionLocal()

    try:
        api_user = create_api_user_service(
            db=db,
            username=username,
            token=token,
            role=role,
        )

        print("\nAPI user created successfully.")
        print(f"Username: {api_user.username}")
        print(f"Role: {api_user.role}")
        print(f"Token: {api_user.token}")

    finally:
        db.close()


if __name__ == "__main__":
    main()