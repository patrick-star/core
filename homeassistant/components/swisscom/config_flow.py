"""Config flow for Swisscom Internet Box integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_HOST, CONF_SSL, CONF_VERIFY_SSL
from homeassistant.data_entry_flow import FlowResult

from .const import DEFAULT_HOST, DEFAULT_SSL, DEFAULT_VERIFY_SSL, DOMAIN


class SwisscomInternetBoxConfigFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle config flow for Swisscom Internet Box."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Prepare user initiated config flow."""
        errors: dict[str, str] = {}
        if user_input is not None:
            return self.async_create_entry(title="Swisscom", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
                    vol.Required(CONF_SSL, default=DEFAULT_SSL): bool,
                    vol.Required(CONF_VERIFY_SSL, default=DEFAULT_VERIFY_SSL): bool,
                }
            ),
            errors=errors,
        )
