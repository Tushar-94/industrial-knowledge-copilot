"""Load and validate NovaTech canonical YAML data."""

from __future__ import annotations

from pathlib import Path

from typing import TypeVar

import yaml

from pydantic import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)

def load_yaml_model(

    path: Path,

    model_type: type[ModelT],

) -> ModelT:

    """Load a YAML file and validate it using a Pydantic model.

    Args:

        path: YAML file to read.

        model_type: Pydantic model used to validate the loaded data.

    Returns:

        A validated Pydantic model instance.

    Raises:

        FileNotFoundError: If the YAML file does not exist.

        ValueError: If the YAML document is empty or its top level is not a

            mapping.

        yaml.YAMLError: If the YAML syntax is invalid.

        pydantic.ValidationError: If loaded data violates the model schema.

    """

    if not path.is_file():

        raise FileNotFoundError(f"Canonical data file not found: {path}")

    with path.open("r", encoding="utf-8") as file:

        raw_data = yaml.safe_load(file)

    if raw_data is None:

        raise ValueError(f"Canonical data file is empty: {path}")

    if not isinstance(raw_data, dict):

        raise ValueError(

            "Canonical YAML must contain a top-level mapping. "

            f"Received {type(raw_data).__name__} in {path}."

        )

    return model_type.model_validate(raw_data)
