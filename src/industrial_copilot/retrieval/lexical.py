"""BM25 lexical retrieval for exact-term and keyword matching."""

from __future__ import annotations

import re

from dataclasses import dataclass

import numpy as np

from rank_bm25 import BM25Okapi

from industrial_copilot.retrieval.models import Chunk

TOKEN_PATTERN = re.compile(

    r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*"

)

@dataclass(frozen=True)

class LexicalSearchResult:

    """One ranked BM25 search result."""

    chunk: Chunk

    score: float

def tokenize(text: str) -> list[str]:

    """Tokenize text while preserving identifiers such as HX-417."""

    return [

        token.lower()

        for token in TOKEN_PATTERN.findall(text)

    ]

class BM25Retriever:

    """Search chunks using BM25 lexical relevance."""

    def __init__(

        self,

        chunks: list[Chunk],

    ) -> None:

        if not chunks:

            raise ValueError(

                "BM25Retriever requires at least one chunk."

            )

        self.chunks = chunks

        self.tokenized_corpus = [

            tokenize(chunk.embedding_text)

            for chunk in chunks

        ]

        self.index = BM25Okapi(

            self.tokenized_corpus

        )

    def search(

        self,

        query: str,

        top_k: int = 5,

    ) -> list[LexicalSearchResult]:

        """Return the highest-scoring BM25 chunks."""

        if top_k <= 0:

            raise ValueError(

                "top_k must be greater than zero."

            )

        query_tokens = tokenize(query)

        scores = self.index.get_scores(

            query_tokens

        )

        ranked_indices = (

            np.argsort(scores)[::-1][:top_k]

        )

        return [

            LexicalSearchResult(

                chunk=self.chunks[index],

                score=float(scores[index]),

            )

            for index in ranked_indices

        ]