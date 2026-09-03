"""Inspect creation of the local Qdrant collection."""

from __future__ import annotations

from industrial_copilot.vector_store.client import (

    create_qdrant_client,

    ensure_collection,

)

from industrial_copilot.vector_store.config import (

    COLLECTION_NAME,

    QDRANT_STORAGE_PATH,

)

def main() -> None:

    """Create and inspect the local Qdrant collection."""

    client = create_qdrant_client()

    ensure_collection(client)

    collection = client.get_collection(

        collection_name=COLLECTION_NAME

    )

    print("Qdrant local database")

    print("=" * 60)

    print(f"Storage path: {QDRANT_STORAGE_PATH}")

    print(f"Collection: {COLLECTION_NAME}")

    print(f"Points: {collection.points_count}")

    print(f"Status: {collection.status}")

if __name__ == "__main__":

    main()
