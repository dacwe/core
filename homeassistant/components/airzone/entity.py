"""Entity classes for the Airzone integration."""
from __future__ import annotations

from typing import Any

from aioairzone.const import (
    AZD_FIRMWARE,
    AZD_FULL_NAME,
    AZD_ID,
    AZD_MODEL,
    AZD_NAME,
    AZD_SYSTEM,
    AZD_SYSTEMS,
    AZD_THERMOSTAT_FW,
    AZD_THERMOSTAT_MODEL,
    AZD_ZONES,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import AirzoneUpdateCoordinator


class AirzoneEntity(CoordinatorEntity[AirzoneUpdateCoordinator]):
    """Define an Airzone entity."""

    def get_airzone_value(self, key: str) -> Any:
        """Return Airzone entity value by key."""
        raise NotImplementedError()


class AirzoneSystemEntity(AirzoneEntity):
    """Define an Airzone System entity."""

    def __init__(
        self,
        coordinator: AirzoneUpdateCoordinator,
        entry: ConfigEntry,
        system_data: dict[str, Any],
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)

        self.system_id = system_data[AZD_ID]

        self._attr_device_info: DeviceInfo = {
            "identifiers": {(DOMAIN, f"{entry.entry_id}_{self.system_id}")},
            "manufacturer": MANUFACTURER,
            "model": self.get_airzone_value(AZD_MODEL),
            "name": self.get_airzone_value(AZD_FULL_NAME),
            "sw_version": self.get_airzone_value(AZD_FIRMWARE),
            "via_device": (DOMAIN, f"{entry.entry_id}_ws"),
        }
        self._attr_unique_id = (
            entry.entry_id if entry.unique_id is None else entry.unique_id
        )

    def get_airzone_value(self, key: str) -> Any:
        """Return system value by key."""
        value = None
        if system := self.coordinator.data[AZD_SYSTEMS].get(self.system_id):
            if key in system:
                value = system[key]
        return value


class AirzoneZoneEntity(AirzoneEntity):
    """Define an Airzone Zone entity."""

    def __init__(
        self,
        coordinator: AirzoneUpdateCoordinator,
        entry: ConfigEntry,
        system_zone_id: str,
        zone_data: dict[str, Any],
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)

        self.system_id = zone_data[AZD_SYSTEM]
        self.system_zone_id = system_zone_id
        self.zone_id = zone_data[AZD_ID]

        self._attr_device_info: DeviceInfo = {
            "identifiers": {(DOMAIN, f"{entry.entry_id}_{system_zone_id}")},
            "manufacturer": MANUFACTURER,
            "model": self.get_airzone_value(AZD_THERMOSTAT_MODEL),
            "name": f"Airzone [{system_zone_id}] {zone_data[AZD_NAME]}",
            "sw_version": self.get_airzone_value(AZD_THERMOSTAT_FW),
            "via_device": (DOMAIN, f"{entry.entry_id}_{self.system_id}"),
        }
        self._attr_unique_id = (
            entry.entry_id if entry.unique_id is None else entry.unique_id
        )

    def get_airzone_value(self, key: str) -> Any:
        """Return zone value by key."""
        value = None
        if zone := self.coordinator.data[AZD_ZONES].get(self.system_zone_id):
            if key in zone:
                value = zone[key]
        return value
