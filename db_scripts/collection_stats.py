from database.qdrant_client_manager import client
from configuration.config import COLLECTION_NAME

from database.qdrant_client_manager import client
from configuration.config import COLLECTION_NAME

def print_collection_stats() -> None:
    """
    Print basic stats for the configured Qdrant collection.
    """
    info = client.get_collection(COLLECTION_NAME)

    print("\nCollection Statistics\n")
    print(f"Name : {COLLECTION_NAME}")
    print(f"Vectors : {info.points_count}")
    print(f"Status : {info.status}")

if __name__ == "__main__":
    print_collection_stats()
