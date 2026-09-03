"""Inspect a point stored in the local Qdrant collection."""

from __future__ import annotations

from industrial_copilot.vector_store.client import (

    create_qdrant_client,

)

from industrial_copilot.vector_store.config import (

    COLLECTION_NAME,

)

def main() -> None:

    """Print one stored Qdrant point and its payload."""

    client = create_qdrant_client()

    points, _ = client.scroll(

        collection_name=COLLECTION_NAME,

        limit=1,

        with_payload=True,

        with_vectors=True,

    )

    if not points:

        raise RuntimeError(

            "The Qdrant collection contains no points."

        )

    point = points[0]

    print("Stored Qdrant Point")

    print("=" * 80)

    print(f"Qdrant ID: {point.id}")

    print()

    print("Payload")

    print("-" * 80)

    for key, value in point.payload.items():

        print(f"{key}: {value}")

    print()

    print("Vector")

    print("-" * 80)

    vector = point.vector

    print(f"Vector dimension: {len(vector)}")

    print(f"First 10 values: {vector[:10]}")

if __name__ == "__main__":

    main()
