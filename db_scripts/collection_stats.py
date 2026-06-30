from database.qdrant_client_manager import client
from configuration.app_settings import COLLECTION_NAME

info = client.get_collection(
    COLLECTION_NAME
)

print("\nCollection Statistics\n")

print(f"Name : {COLLECTION_NAME}")

print(f"Vectors : {info.points_count}")

print(f"Status : {info.status}")