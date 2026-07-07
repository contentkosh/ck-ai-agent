from qdrant_client.models import (
    Distance,
    VectorParams,
)
from qdrant_client.http.exceptions import UnexpectedResponse

from common.logger import logger

from database.qdrant_client_manager import client

from configuration.app_settings import (
    COLLECTION_NAME,
    EMBEDDING_DIMENSION,
)

from common.custom_exceptions import DatabaseException


"""
Create the Knowledge Base collection.

This collection stores document embeddings generated during
the ingestion process. The embeddings are used for semantic
search and Retrieval-Augmented Generation (RAG).
"""


try:

    if not client.collection_exists(COLLECTION_NAME):

        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=EMBEDDING_DIMENSION,
                distance=Distance.COSINE,
            ),
        )

        logger.info(
            "Collection '%s' created successfully.",
            COLLECTION_NAME,
        )

    else:

        logger.info(
            "Collection '%s' already exists.",
            COLLECTION_NAME,
        )

except UnexpectedResponse as ex:

    logger.exception(
        "Failed to create Knowledge Base collection."
    )

    raise DatabaseException(
        "Unable to create Knowledge Base collection."
    ) from ex