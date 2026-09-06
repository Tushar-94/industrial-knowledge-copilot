"""Inspect a Qdrant point containing HX-417 metadata."""

from __future__ import annotations

from industrial_copilot.vector_store.client import (

    create_qdrant_client,

)

from industrial_copilot.vector_store.config import (

    COLLECTION_NAME,

)

def main() -> None:

    client = create_qdrant_client()

    points, _ = client.scroll(

        collection_name=COLLECTION_NAME,

        with_payload=True,

        with_vectors=False,

        limit=200,

    )

    point = next(

        point

        for point in points

        if (

            point.payload

            and "HX-417"

            in point.payload.get(

                "alarm_codes",

                [],

            )

        )

    )

    print("Qdrant alarm point")

    print("=" * 80)

    print("point_id:", point.id)

    print(

        "chunk_id:",

        point.payload["chunk_id"],

    )

    print(

        "document_id:",

        point.payload["document_id"],

    )

    print(

        "section_title:",

        point.payload["section_title"],

    )

    print(

        "alarm_codes:",

        point.payload["alarm_codes"],

    )

    print(

        "related_procedures:",

        point.payload["related_procedures"],

    )

    print(

        "related_components:",

        point.payload["related_components"],

    )

if __name__ == "__main__":

    main()
