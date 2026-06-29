"""Tests for the Swegon GENIUS integration."""  # noqa: INP001

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.const import CONF_PORT

from custom_components.swegon_genius.const import (
    CONF_BAUDRATE,
    CONF_PARITY,
    CONF_SLAVE,
    CONF_STOPBITS,
    DOMAIN,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


USER_INPUT = {
    CONF_PORT: "/dev/ttyUSB0",
    CONF_SLAVE: 1,
    CONF_BAUDRATE: 38400,
    CONF_STOPBITS: 1,
    CONF_PARITY: "N",
}


@pytest.mark.asyncio
async def test_show_form(hass: HomeAssistant) -> None:
    """Test initial form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] == "form"
    assert result["step_id"] == "user"


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
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input=USER_INPUT,
        )

        assert result["type"] == "create_entry"
        assert result["title"] == "Swegon CASA Genius (/dev/ttyUSB0)"
        assert result["data"] == USER_INPUT

        instance.connect.assert_awaited_once()
        instance.disconnect.assert_awaited_once()


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
            user_input=USER_INPUT,
        )

        assert result["type"] == "form"
        assert result["errors"] == {"base": "cannot_connect"}

        instance.disconnect.assert_awaited_once()


@pytest.mark.asyncio
async def test_connection_exception(hass: HomeAssistant) -> None:
    """Test exception during connection."""
    with patch(
        "custom_components.swegon_genius.config_flow.SwegonModbusClient"
    ) as mock_client:
        instance = mock_client.return_value
        instance.connect = AsyncMock(side_effect=RuntimeError("connection error"))
        instance.disconnect = AsyncMock()

        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input=USER_INPUT
        )

        assert result["type"] == "form"
        assert result["errors"] == {"base": "cannot_connect"}

        instance.disconnect.assert_awaited_once()


@pytest.mark.asyncio
async def test_duplicate_configuration(hass: HomeAssistant) -> None:
    """Test duplicate configuration entries, which should abort."""
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
        await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input=USER_INPUT,
        )
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input=USER_INPUT,
        )

        assert result["type"] == "abort"
        assert result["reason"] == "already_configured"


@pytest.mark.parametrize(
    ("baudrate", "stopbits", "parity"),
    [
        (9600, 1, "N"),
        (19200, 2, "E"),
        (38400, 1, "O"),
        (57600, 2, "N"),
        (115200, 1, "E"),
    ],
)
@pytest.mark.asyncio
async def test_serial_settings(
    hass: HomeAssistant, baudrate: int, stopbits: int, parity: str
) -> None:
    """Supported serial settings are accepted."""
    with patch(
        "custom_components.swegon_genius.config_flow.SwegonModbusClient"
    ) as mock_client:
        instance = mock_client.return_value
        instance.connect = AsyncMock(return_value=True)
        instance.disconnect = AsyncMock()

        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        user_input = dict(USER_INPUT)
        user_input[CONF_BAUDRATE] = baudrate
        user_input[CONF_STOPBITS] = stopbits
        user_input[CONF_PARITY] = parity
        user_input[CONF_PORT] = f"/dev/ttyUSB{baudrate}"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input=user_input
        )

    assert result["type"] == "create_entry"
