"""Constants for the PandaScore R6 Siege integration."""

from homeassistant.const import Platform

DOMAIN = "pandascore_r6"

CONF_UPDATE_INTERVAL = "update_interval"

DEFAULT_UPDATE_INTERVAL_MINUTES = 5
MIN_UPDATE_INTERVAL_MINUTES = 1
MAX_UPDATE_INTERVAL_MINUTES = 1440

API_BASE_URL = "https://api.pandascore.co"
UPCOMING_MATCHES_PATH = "/r6siege/matches/upcoming"

PLATFORMS = [Platform.SENSOR]
