"""Embedding utilities for retrieval chunks and user queries."""

from __future__ import annotations

import numpy as np

from numpy.typing import NDArray

from sentence_transformers import SentenceTransformer

from industrial_copilot.retrieval.models import Chunk

DEFAULT_EMBEDDING_MODEL = (

    "sentence-transformers/all-MiniLM-L6-v2"

)

class Embedder:

    """Convert chunk text and user queries into dense vectors."""

    def __init__(

        self,

        model_name: str = DEFAULT_EMBEDDING_MODEL,

    ) -> None:

        self.model_name = model_name

        self.model = SentenceTransformer(model_name)

    @property

    def embedding_dimension(self) -> int:

        """Return the output-vector dimension."""

        dimension = self.model.get_embedding_dimension()

        if dimension is None:

            raise ValueError(

                "Embedding model did not report an embedding dimension."

            )

        return dimension

    @property

    def max_sequence_length(self) -> int:

        """Return the configured maximum input sequence length."""

        return self.model.max_seq_length

    def embed_chunks(

        self,

        chunks: list[Chunk],

    ) -> NDArray[np.float32]:

        """Embed retrieval chunks using their embedding text."""

        texts = [

            chunk.embedding_text

            for chunk in chunks

        ]

        embeddings = self.model.encode(

            texts,

            convert_to_numpy=True,

            normalize_embeddings=True,

        )

        return embeddings.astype(np.float32)

    def embed_query(

        self,

        query: str,

    ) -> NDArray[np.float32]:

        """Embed one user query."""

        embedding = self.model.encode(

            query,

            convert_to_numpy=True,

            normalize_embeddings=True,

        )

        return embedding.astype(np.float32)
