from common.logger import logger

from configuration.config import (
    COLLECTION_NAME,
)

from configuration.constants import (
    COLLECTION_STATS_HEADER_LOG,
    COLLECTION_STATS_LOG,
)

from database.qdrant_client_manager import client


def print_collection_stats() -> None:
    """
    Print basic stats for the configured Qdrant collection.
    """
    collectionInfo = client.get_collection(
        COLLECTION_NAME,
    )

    logger.info(
        COLLECTION_STATS_HEADER_LOG,
    )

    logger.info(
        COLLECTION_STATS_LOG,
        COLLECTION_NAME,
        collectionInfo.points_count,
        collectionInfo.status,
    )


if __name__ == "__main__":
    print_collection_stats()