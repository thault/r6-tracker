"""Data update coordinator for the PandaScore R6 Siege integration."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import (
    PandaScoreApiClient,
    PandaScoreApiError,
    PandaScoreAuthError,
    PandaScoreRateLimitError,
)
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


@dataclass
class Opponent:
    """A team competing in a match."""

    name: str
    acronym: str | None
    image_url: str | None


@dataclass
class Stream:
    """A broadcast stream for a match."""

    language: str | None
    url: str | None
    official: bool


@dataclass
class NextMatchData:
    """The next upcoming R6 Siege pro match."""

    match_id: int
    name: str
    begin_at: datetime
    league_name: str | None
    serie_name: str | None
    tournament_name: str | None
    best_of: int | None
    status: str
    opponents: list[Opponent] = field(default_factory=list)
    streams: list[Stream] = field(default_factory=list)


def _parse_match(match: dict) -> NextMatchData:
    begin_at_raw = match.get("begin_at") or match.get("scheduled_at")
    begin_at = dt_util.parse_datetime(begin_at_raw) if begin_at_raw else dt_util.utcnow()

    opponents = [
        Opponent(
            name=o["opponent"]["name"],
            acronym=o["opponent"].get("acronym"),
            image_url=o["opponent"].get("image_url"),
        )
        for o in match.get("opponents", [])
        if o.get("opponent")
    ]

    streams = [
        Stream(
            language=s.get("language"),
            url=s.get("raw_url") or s.get("embed_url"),
            official=bool(s.get("official")),
        )
        for s in match.get("streams_list", [])
    ]

    league = match.get("league") or {}
    serie = match.get("serie") or {}
    tournament = match.get("tournament") or {}

    return NextMatchData(
        match_id=match["id"],
        name=match.get("name", ""),
        begin_at=begin_at,
        league_name=league.get("name"),
        serie_name=serie.get("full_name"),
        tournament_name=tournament.get("name"),
        best_of=match.get("number_of_games"),
        status=match.get("status", "unknown"),
        opponents=opponents,
        streams=streams,
    )


class PandaScoreR6Coordinator(DataUpdateCoordinator[NextMatchData | None]):
    """Coordinator that polls PandaScore for the next upcoming R6 Siege match."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        client: PandaScoreApiClient,
        update_interval: timedelta,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=entry,
            update_interval=update_interval,
        )
        self._client = client

    async def _async_update_data(self) -> NextMatchData | None:
        try:
            matches = await self._client.async_get_upcoming_matches(per_page=5)
        except PandaScoreAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except PandaScoreRateLimitError as err:
            raise UpdateFailed(f"Rate limited by PandaScore: {err}") from err
        except PandaScoreApiError as err:
            raise UpdateFailed(str(err)) from err

        upcoming = sorted(
            matches, key=lambda m: m.get("begin_at") or m.get("scheduled_at") or ""
        )
        for match in upcoming:
            if match.get("status") == "not_started":
                return _parse_match(match)

        return None


type PandaScoreR6ConfigEntry = ConfigEntry[PandaScoreR6Coordinator]
