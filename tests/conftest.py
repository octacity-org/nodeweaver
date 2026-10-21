"""Shared pytest fixtures."""

from pathlib import Path

import pytest

EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples"


@pytest.fixture
def examples_dir() -> Path:
    """Path to the examples/ folder with the sample projects."""
    return EXAMPLES_DIR
