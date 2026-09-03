"""Configuration for the local Qdrant vector store."""

from __future__ import annotations

from pathlib import Path

COLLECTION_NAME = "industrial_knowledge"

EMBEDDING_DIMENSION = 384

QDRANT_STORAGE_PATH = (

    Path(__file__).resolve().parents[3]

    / ".qdrant"

)
