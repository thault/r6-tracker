"""Sensor platform for the PandaScore R6 Siege integration."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import PandaScoreR6ConfigEntry, PandaScoreR6Coordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PandaScoreR6ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the next-match sensor from a config entry."""
    async_add_entities([NextR6MatchSensor(entry.runtime_data)])


class NextR6MatchSensor(CoordinatorEntity[PandaScoreR6Coordinator], SensorEntity):
    """Sensor exposing the next upcoming R6 Siege pro match."""

    _attr_has_entity_name = False
    _attr_name = "Next R6 Pro Match"
    _attr_unique_id = f"{DOMAIN}_next_match"
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:controller"

    @property
    def native_value(self) -> datetime | None:
        """Return the start time of the next match."""
        match = self.coordinator.data
        return match.begin_at if match else None

    @property
    def available(self) -> bool:
        """Return whether a next match is currently known."""
        return super().available and self.coordinator.data is not None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return details about the next match."""
        match = self.coordinator.data
        if match is None:
            return {}

        return {
            "pandascore_match_id": match.match_id,
            "match_name": match.name,
            "league": match.league_name,
            "serie": match.serie_name,
            "tournament": match.tournament_name,
            "best_of": match.best_of,
            "status": match.status,
            "teams": [opponent.name for opponent in match.opponents],
            "opponents": [
                {
                    "name": opponent.name,
                    "acronym": opponent.acronym,
                    "image_url": opponent.image_url,
                }
                for opponent in match.opponents
            ],
            "stream_urls": [
                {
                    "language": stream.language,
                    "url": stream.url,
                    "official": stream.official,
                }
                for stream in match.streams
            ],
        }
