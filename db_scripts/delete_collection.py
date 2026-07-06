from common.logger import logger
from configuration.config import COLLECTION_NAME
from configuration.constants import (COLLECTION_DELETED_SUCCESS_LOG,)
from database.qdrant_client_manager import client
def delete_collection() -> None:
    """
    Delete the Qdrant collection.
    """
    client.delete_collection(COLLECTION_NAME)
    logger.info(
        COLLECTION_DELETED_SUCCESS_LOG,
        COLLECTION_NAME,
    )
if __name__ == "__main__":
    delete_collection()
