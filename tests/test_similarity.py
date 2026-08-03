"""Tests for vector-similarity utilities."""

from __future__ import annotations

import numpy as np

import pytest

from industrial_copilot.embeddings.similarity import cosine_similarity

def test_identical_vectors_have_similarity_one() -> None:

    vector = np.array([1.0, 2.0, 3.0])

    result = cosine_similarity(vector, vector)

    assert result == pytest.approx(1.0)

def test_perpendicular_vectors_have_similarity_zero() -> None:

    vector_a = np.array([1.0, 0.0])

    vector_b = np.array([0.0, 1.0])

    result = cosine_similarity(vector_a, vector_b)

    assert result == pytest.approx(0.0)

def test_opposite_vectors_have_similarity_negative_one() -> None:

    vector_a = np.array([1.0, 0.0])

    vector_b = np.array([-1.0, 0.0])

    result = cosine_similarity(vector_a, vector_b)

    assert result == pytest.approx(-1.0)

def test_zero_vector_raises_value_error() -> None:

    zero_vector = np.array([0.0, 0.0])

    valid_vector = np.array([1.0, 1.0])

    with pytest.raises(

        ValueError,

        match="undefined for a zero vector",

    ):

        cosine_similarity(zero_vector, valid_vector)

def test_mismatched_shapes_raise_value_error() -> None:

    vector_a = np.array([1.0, 2.0])

    vector_b = np.array([1.0, 2.0, 3.0])

    with pytest.raises(

        ValueError,

        match="same shape",

    ):

        cosine_similarity(vector_a, vector_b)
