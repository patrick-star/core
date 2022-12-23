"""Support for Swisscom routers (Internet-Box)."""
from __future__ import annotations

from contextlib import suppress
import logging

import requests

from homeassistant.components.device_tracker import DeviceScanner
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_SSL, CONF_VERIFY_SSL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Prepare setup of Swisscom Internet Box device scanner."""
    logging.debug("Swisscom")
    # config = hass.data[DOMAIN][config_entry.entry_id]
    # scanner = await hass.async_add_executor_job(SwisscomDeviceScanner, config)
    # if scanner.success_init:
    #     async_add_entities([scanner])


class SwisscomDeviceScanner(DeviceScanner):
    """This class queries a router running Swisscom Internet-Box firmware."""

    def __init__(self, config) -> None:
        """Initialize the scanner."""
        self.host = config[CONF_HOST]
        self.protocol = "https" if config[CONF_SSL] else "http"
        self.verify_ssl = config[CONF_VERIFY_SSL]
        self.last_results: dict = {}
        # Test if  the router is accessible.
        data = self.get_swisscom_data()
        self.success_init = data is not None

    def scan_devices(self):
        """Scan for new devices and return a list with found device IDs."""
        self._update_info()
        return [client["mac"] for client in self.last_results]

    def get_device_name(self, device):
        """Return the name of the given device or None if we don't know."""
        if not self.last_results:
            return None
        for client in self.last_results:
            if client["mac"] == device:
                return client["host"]
        return None

    def _update_info(self):
        """Ensure the information from the Swisscom router is up to date.

        Return boolean if scanning successful.
        """
        if not self.success_init:
            return False

        _LOGGER.info("Loading data from Swisscom Internet Box")
        if not (data := self.get_swisscom_data()):
            return False

        active_clients = [client for client in data.values() if client["status"]]
        self.last_results = active_clients
        return True

    def get_swisscom_data(self):
        """Retrieve data from Swisscom and return parsed result."""
        url = f"{self.protocol}://{self.host}/ws"
        headers = {"Content-Type": "application/x-sah-ws-4-call+json"}
        data = """
        {"service":"Devices", "method":"get",
        "parameters":{"expression":"lan and not self"}}"""

        devices = {}
        request = None
        try:
            request = requests.post(
                url, headers=headers, data=data, timeout=5, verify=self.verify_ssl
            )
        except requests.exceptions.ReadTimeout:
            _LOGGER.error("No response from Swisscom Internet Box")
        except requests.exceptions.Timeout:
            _LOGGER.error("Timeout during connection to Swisscom Internet Box")
        except requests.exceptions.SSLError:
            _LOGGER.error("SSL error during connection to Swisscom Internet Box")
        except requests.exceptions.ConnectionError:
            _LOGGER.error("Unspecific error during connection to Swisscom Internet Box")
        except requests.exceptions.RequestException:
            _LOGGER.error("Unspecific error during request")
        else:
            if "status" not in request.json():
                _LOGGER.info("No status in response from Swisscom Internet Box")
                return devices

            for device in request.json()["status"]:
                with suppress(KeyError, requests.exceptions.RequestException):
                    devices[device["Key"]] = {
                        "ip": device["IPAddress"],
                        "mac": device["PhysAddress"],
                        "host": device["Name"],
                        "status": device["Active"],
                    }
        return devices
