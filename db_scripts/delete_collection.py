from common.logger import logger
from configuration.constants import (
    COLLECTION_DELETED_SUCCESS_LOG,
)
from database.qdrant_client_manager import client
from common.collection_utils import (
    get_kb_collection_name,
)

def delete_collection(
    business_id: str,
) -> None:
    """
    Delete the Knowledge Base Qdrant collection belonging
    to the specified business.
    """
    collection_name = get_kb_collection_name(
        business_id,
    )
    client.delete_collection(
        collection_name,
    )
    logger.info(
        COLLECTION_DELETED_SUCCESS_LOG,
        collection_name,
    )

if __name__ == "__main__":
    logger.info(
        "Business ID is required to delete a collection."
    )