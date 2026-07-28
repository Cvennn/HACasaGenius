# Copyright (c) 2026  Antti Niiranen @Cvennn # noqa: INP001

"""Quality-scale related regression tests."""

from importlib import import_module

import pytest


@pytest.mark.parametrize(
    "module_name",
    [
        "custom_components.swegon_genius.binary_sensor",
        "custom_components.swegon_genius.button",
        "custom_components.swegon_genius.number",
        "custom_components.swegon_genius.select",
        "custom_components.swegon_genius.sensor",
        "custom_components.swegon_genius.switch",
    ],
)
def test_platform_modules_limit_parallel_updates(module_name: str) -> None:
    """Each platform module should make parallel updates explicit."""
    module = import_module(module_name)

    assert getattr(module, "PARALLEL_UPDATES", None) == 1
