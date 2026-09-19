"""The PandaScore R6 Siege integration."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import PandaScoreApiClient
from .const import CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL_MINUTES, PLATFORMS
from .coordinator import PandaScoreR6ConfigEntry, PandaScoreR6Coordinator


async def async_setup_entry(hass: HomeAssistant, entry: PandaScoreR6ConfigEntry) -> bool:
    """Set up PandaScore R6 Siege from a config entry."""
    client = PandaScoreApiClient(
        async_get_clientsession(hass), entry.data[CONF_API_KEY]
    )

    update_interval = timedelta(
        minutes=entry.options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL_MINUTES)
    )

    coordinator = PandaScoreR6Coordinator(hass, entry, client, update_interval)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: PandaScoreR6ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_reload_entry(hass: HomeAssistant, entry: PandaScoreR6ConfigEntry) -> None:
    """Reload the config entry when its options change."""
    await hass.config_entries.async_reload(entry.entry_id)
