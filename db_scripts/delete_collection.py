from fastapi import logger
from qdrant_client import QdrantClient
from configuration.app_settings import COLLECTION_NAME

client = QdrantClient(host="localhost",port=6333)
client.delete_collection(COLLECTION_NAME)
logger.info(f"Collection '{COLLECTION_NAME}' deleted successfully.")