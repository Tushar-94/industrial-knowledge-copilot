"""Index retrieval chunks and embeddings into Qdrant."""

from __future__ import annotations

from uuid import NAMESPACE_URL, uuid5

import numpy as np

from numpy.typing import NDArray

from qdrant_client import QdrantClient

from qdrant_client.models import PointStruct

from industrial_copilot.retrieval.models import Chunk

from industrial_copilot.vector_store.config import (

    COLLECTION_NAME,

)

def _point_id_from_chunk_id(

    chunk_id: str,

) -> str:

    """Create a stable Qdrant UUID from a human-readable chunk ID."""

    return str(

        uuid5(

            NAMESPACE_URL,

            chunk_id,

        )

    )

def _chunk_payload(

    chunk: Chunk,

) -> dict[str, object]:

    """Convert chunk metadata into a Qdrant payload."""

    return {

        "chunk_id": chunk.chunk_id,

        "document_id": chunk.document_id,

        "document_type": chunk.document_type,

        "machine_models": chunk.machine_models,

        "section_title": chunk.section_title,

        "heading_path": chunk.heading_path,

        "revision": chunk.revision,

        "effective_date": chunk.effective_date.isoformat(),

        "language": chunk.language,

        "text": chunk.text,

        "embedding_text": chunk.embedding_text,

    }

def build_points(

    *,

    chunks: list[Chunk],

    embeddings: NDArray[np.float32],

) -> list[PointStruct]:

    """Convert chunks and embeddings into Qdrant points."""

    if len(chunks) != len(embeddings):

        raise ValueError(

            "Number of chunks must match number of embeddings."

        )

    points: list[PointStruct] = []

    for chunk, embedding in zip(

        chunks,

        embeddings,

        strict=True,

    ):

        points.append(

            PointStruct(

                id=_point_id_from_chunk_id(

                    chunk.chunk_id

                ),

                vector=embedding.tolist(),

                payload=_chunk_payload(chunk),

            )

        )

    return points

def index_chunks(

    *,

    client: QdrantClient,

    chunks: list[Chunk],

    embeddings: NDArray[np.float32],

) -> None:

    """Upsert chunk points into Qdrant."""

    points = build_points(

        chunks=chunks,

        embeddings=embeddings,

    )

    client.upsert(

        collection_name=COLLECTION_NAME,

        points=points,

        wait=True,

    )
