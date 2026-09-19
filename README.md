# R6 Siege Pro Schedule

A Home Assistant custom integration that exposes when the next Rainbow Six
Siege pro esports match is, as a native sensor.

## What you get

A single entity, `sensor.next_r6_pro_match`, whose state is the start time of
the next upcoming pro match (any league/tournament), with attributes:

- `match_name`, `league`, `serie`, `tournament`, `best_of`, `status`
- `teams` — flat list of team names
- `opponents` — full list of `{name, acronym, image_url}`
- `stream_urls` — list of `{language, url, official}`
- `pandascore_match_id`

Because the sensor's `device_class` is `timestamp`, it works directly with
Home Assistant's relative-time formatting (`relative_time()`) and countdown
cards/automations.

## Data source

Match data comes from [PandaScore](https://pandascore.co)'s free API tier,
which includes schedule/results data at no cost (no credit card required).

1. Create a free account at [pandascore.co](https://pandascore.co).
2. Generate an API token from your PandaScore dashboard.
3. Use that token when setting up this integration in Home Assistant.

The free tier allows 1,000 requests/hour. Even at this integration's fastest
allowed poll interval (1 minute = 60 requests/hour), you're well within that
limit.

## Installation (HACS)

1. In HACS, add this repository as a custom repository (category:
   Integration): `https://github.com/thault/r6-tracker`.
2. Install "R6 Siege Pro Schedule (PandaScore)".
3. Restart Home Assistant.
4. Go to **Settings → Devices & Services → Add Integration**, search for
   "R6 Siege Pro Schedule", and enter your PandaScore API token.

## Options

After setup, click **Configure** on the integration to change the poll
interval (in minutes). Minimum: 1 minute. Default: 5 minutes.

## License

MIT
