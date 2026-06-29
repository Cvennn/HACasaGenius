"""Tests for the Swegon GENIUS integration."""  # noqa: EXE002, INP001

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant import config_entries

from custom_components.swegon_genius.const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


@pytest.mark.asyncio
async def test_config_flow_success(hass: HomeAssistant) -> None:
    """Test a successful config flow."""
    with patch(
        "custom_components.swegon_genius.config_flow.SwegonModbusClient"
    ) as mock_client:
        instance = mock_client.return_value
        instance.connect = AsyncMock(return_value=True)
        instance.disconnect = AsyncMock()

        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
        )

        assert result["type"] == "form"  # pyright: ignore[reportTypedDictNotRequiredAccess] # noqa: S101

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={
                "port": "/dev/ttyUSB0",
                "slave": 1,
                "baudrate": 38400,
                "stopbits": 1,
                "parity": "N",
            },
        )

        assert result["type"] == "create_entry"  # pyright: ignore[reportTypedDictNotRequiredAccess] # noqa: S101
        assert result["title"] == "Swegon CASA Genius (/dev/ttyUSB0)"  # pyright: ignore[reportTypedDictNotRequiredAccess] # noqa: S101
        assert result["data"]["port"] == "/dev/ttyUSB0"  # pyright: ignore[reportTypedDictNotRequiredAccess] # noqa: S101
        assert result["data"]["slave"] == 1  # pyright: ignore[reportTypedDictNotRequiredAccess] # noqa: S101


@pytest.mark.asyncio
async def test_config_flow_cannot_connect(hass: HomeAssistant) -> None:
    """Test connection failure."""
    with patch(
        "custom_components.swegon_genius.config_flow.SwegonModbusClient"
    ) as mock_client:
        instance = mock_client.return_value
        instance.connect = AsyncMock(return_value=False)
        instance.disconnect = AsyncMock()

        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={
                "port": "/dev/ttyUSB0",
                "slave": 1,
                "baudrate": 38400,
                "stopbits": 1,
                "parity": "N",
            },
        )

        assert result["type"] == "form"  # pyright: ignore[reportTypedDictNotRequiredAccess] # noqa: S101
        assert result["errors"] == {"base": "cannot_connect"}  # pyright: ignore[reportTypedDictNotRequiredAccess] # noqa: S101
