from common.logger import logger
from configuration.constants import (
    COLLECTION_STATS_HEADER_LOG,
    COLLECTION_STATS_LOG,
)
from database.qdrant_client_manager import client
from common.collection_utils import (
    get_kb_collection_name,
)

def print_collection_stats(
    business_id: str,
) -> None:
    """
    Print basic stats for a specific business's
    Knowledge Base Qdrant collection.
    """

    collection_name = get_kb_collection_name(
        business_id,
    )
    collectionInfo = client.get_collection(
        collection_name,
    )
    logger.info(COLLECTION_STATS_HEADER_LOG)
    logger.info(
        COLLECTION_STATS_LOG,
        collection_name,
        collectionInfo.points_count,
        collectionInfo.status,
    )

if __name__ == "__main__":
    logger.info(
        "Business ID is required to inspect collection stats."
    )