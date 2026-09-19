"""Config flow for the PandaScore R6 Siege integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_API_KEY
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import PandaScoreApiClient, PandaScoreApiError, PandaScoreAuthError
from .const import (
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL_MINUTES,
    DOMAIN,
    MAX_UPDATE_INTERVAL_MINUTES,
    MIN_UPDATE_INTERVAL_MINUTES,
)

STEP_USER_DATA_SCHEMA = vol.Schema({vol.Required(CONF_API_KEY): str})


async def _async_validate_api_key(hass, api_key: str) -> None:
    """Raise PandaScoreAuthError/PandaScoreApiError if the token doesn't work."""
    client = PandaScoreApiClient(async_get_clientsession(hass), api_key)
    await client.async_get_upcoming_matches(per_page=1)


class PandaScoreR6ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for the PandaScore R6 Siege integration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Collect and validate the PandaScore API token."""
        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()

            try:
                await _async_validate_api_key(self.hass, user_input[CONF_API_KEY])
            except PandaScoreAuthError:
                errors["base"] = "invalid_auth"
            except PandaScoreApiError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title="R6 Siege Pro Schedule", data=user_input
                )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_reauth(
        self, entry_data: dict[str, Any]
    ) -> ConfigFlowResult:
        """Handle reauthentication after the token is rejected."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm a new API token during reauth."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await _async_validate_api_key(self.hass, user_input[CONF_API_KEY])
            except PandaScoreAuthError:
                errors["base"] = "invalid_auth"
            except PandaScoreApiError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_update_reload_and_abort(
                    self._get_reauth_entry(), data=user_input
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> PandaScoreR6OptionsFlow:
        """Return the options flow for this handler."""
        return PandaScoreR6OptionsFlow()


class PandaScoreR6OptionsFlow(OptionsFlow):
    """Handle options (poll interval) for the PandaScore R6 Siege integration."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the poll interval option."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        current = self.config_entry.options.get(
            CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL_MINUTES
        )

        schema = vol.Schema(
            {
                vol.Required(CONF_UPDATE_INTERVAL, default=current): vol.All(
                    vol.Coerce(int),
                    vol.Range(
                        min=MIN_UPDATE_INTERVAL_MINUTES, max=MAX_UPDATE_INTERVAL_MINUTES
                    ),
                )
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
