"""Vector-similarity utilities used by the retrieval system."""

from __future__ import annotations

import numpy as np

from numpy.typing import NDArray

def cosine_similarity(

    vector_a: NDArray[np.floating],

    vector_b: NDArray[np.floating],

) -> float:

    """Return the cosine similarity between two one-dimensional vectors.

    Args:

        vector_a: First numeric vector.

        vector_b: Second numeric vector.

    Returns:

        A floating-point cosine-similarity value.

    Raises:

        ValueError: If vectors are not one-dimensional, their shapes differ,

            or either vector has zero magnitude.

    """

    if vector_a.ndim != 1 or vector_b.ndim != 1:

        raise ValueError("Cosine similarity requires one-dimensional vectors.")

    if vector_a.shape != vector_b.shape:

        raise ValueError(

            "Vectors must have the same shape. "

            f"Received {vector_a.shape} and {vector_b.shape}."

        )

    denominator = np.linalg.norm(vector_a) * np.linalg.norm(vector_b)

    if np.isclose(denominator, 0.0):

        raise ValueError("Cosine similarity is undefined for a zero vector.")

    numerator = np.dot(vector_a, vector_b)

    return float(numerator / denominator)
