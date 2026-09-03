"""Create and configure the local Qdrant client."""

from __future__ import annotations

from qdrant_client import QdrantClient

from qdrant_client.models import Distance, VectorParams

from industrial_copilot.vector_store.config import (

    COLLECTION_NAME,

    EMBEDDING_DIMENSION,

    QDRANT_STORAGE_PATH,

)

def create_qdrant_client() -> QdrantClient:

    """Create a persistent local Qdrant client."""

    QDRANT_STORAGE_PATH.mkdir(

        parents=True,

        exist_ok=True,

    )

    return QdrantClient(

        path=str(QDRANT_STORAGE_PATH)

    )

def ensure_collection(

    client: QdrantClient,

) -> None:

    """Create the vector collection when it does not already exist."""

    if client.collection_exists(

        collection_name=COLLECTION_NAME

    ):

        return

    client.create_collection(

        collection_name=COLLECTION_NAME,

        vectors_config=VectorParams(

            size=EMBEDDING_DIMENSION,

            distance=Distance.COSINE,

        ),

    )
