"""Dense semantic retrieval backed by Qdrant."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from numpy.typing import NDArray

from qdrant_client import QdrantClient

from industrial_copilot.vector_store.config import (

    COLLECTION_NAME,

)

from qdrant_client.models import (

    FieldCondition,

    Filter,

    MatchValue,

)

@dataclass(frozen=True)

class QdrantSearchResult:

    """One semantic-search result returned from Qdrant."""

    point_id: str

    score: float

    chunk_id: str

    document_id: str

    document_type: str

    machine_models: list[str]

    section_title: str

    heading_path: list[str]

    revision: str

    effective_date: str

    language: str

    text: str

def search_qdrant(

    *,

    client: QdrantClient,

    query_embedding: NDArray[np.float32],

    top_k: int = 5,

    machine_model: str | None = None,

) -> list[QdrantSearchResult]:

    """Search Qdrant using one dense query embedding."""

    if top_k <= 0:

        raise ValueError(

            "top_k must be greater than zero."

        )

    query_filter = None

    if machine_model is not None:

        query_filter = Filter(

            must=[

                FieldCondition(

                    key="machine_models",

                    match=MatchValue(

                        value=machine_model

                    ),

                )

            ]

        )

    response = client.query_points(

        collection_name=COLLECTION_NAME,

        query=query_embedding.tolist(),

        query_filter=query_filter,

        with_payload=True,

        limit=top_k,

    )

    results: list[QdrantSearchResult] = []

    for point in response.points:

        payload = point.payload or {}

        results.append(

            QdrantSearchResult(

                point_id=str(point.id),

                score=float(point.score),

                chunk_id=str(payload["chunk_id"]),

                document_id=str(payload["document_id"]),

                document_type=str(payload["document_type"]),

                machine_models=list(

                    payload["machine_models"]

                ),

                section_title=str(

                    payload["section_title"]

                ),

                heading_path=list(

                    payload["heading_path"]

                ),

                revision=str(payload["revision"]),

                effective_date=str(

                    payload["effective_date"]

                ),

                language=str(payload["language"]),

                text=str(payload["text"]),

            )

        )

    return results