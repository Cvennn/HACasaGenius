# Copyright (c) 2026  Antti Niiranen @Cvennn # noqa: INP001

"""Pytest configuration and fixtures for HACasaGenius tests."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):  # noqa: ANN001, ANN201, ARG001, D103
    return
