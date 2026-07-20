from database.qdrant_client_manager import client
from configuration.config import COLLECTION_NAME

def delete_collection() -> None:
    """
    Delete the Qdrant collection.
    """
    client.delete_collection(COLLECTION_NAME)
    print(f"Collection '{COLLECTION_NAME}' deleted successfully.")

if __name__ == "__main__":
    delete_collection()