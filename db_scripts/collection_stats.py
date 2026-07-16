from common.logger import logger
from database.qdrant_client_manager import client
from configuration.app_settings import COLLECTION_NAME

try:
    info = client.get_collection(COLLECTION_NAME)
    logger.info("Collection Statistics")
    logger.info("Name : %s", COLLECTION_NAME)
    logger.info("Vectors : %s", info.points_count)
    logger.info("Status : %s", info.status)

except Exception as ex:
    logger.exception("Failed to retrieve collection statistics: %s", ex)