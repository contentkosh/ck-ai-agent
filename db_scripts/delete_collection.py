from database.qdrant_client_manager import client
from configuration.config import (COLLECTION_NAME,)

client.delete_collection(COLLECTION_NAME)
print(f"Collection '{COLLECTION_NAME}' deleted successfully.")