#!/usr/bin/env python3
"""Render /app/data/config.json from ISBTV_* environment variables."""

import json
import os
import sys
from pathlib import Path

CONFIG_PATH = Path(os.environ.get("ISBTV_CONFIG_PATH", "/app/data/config.json"))


def flag(name: str, default: str) -> bool:
    value = os.environ.get(name, default).strip().lower()
    if value not in {"true", "false"}:
        sys.exit(f"{name} must be true or false, got {value!r}")
    return value == "true"


def number(name: str, default: str) -> int:
    value = os.environ.get(name, default).strip()
    try:
        return int(value)
    except ValueError:
        sys.exit(f"{name} must be an integer, got {value!r}")


def csv_list(name: str) -> list[str]:
    return [item.strip() for item in os.environ.get(name, "").split(",") if item.strip()]


screen_id = os.environ.get("ISBTV_SCREEN_ID", "").strip()
if not screen_id:
    sys.exit(
        "ISBTV_SCREEN_ID is empty: pair the device first with scripts/pair.sh and put the "
        "screen id in .env"
    )

categories = csv_list("ISBTV_SKIP_CATEGORIES") or ["sponsor"]
whitelist = csv_list("ISBTV_CHANNEL_WHITELIST")
apikey = os.environ.get("ISBTV_APIKEY", "").strip()
if whitelist and not apikey:
    sys.exit("ISBTV_CHANNEL_WHITELIST needs ISBTV_APIKEY: the app resolves channel ids "
             "through the YouTube Data API and refuses to start without a key")

config = {
    "devices": [
        {
            "screen_id": screen_id,
            "name": os.environ.get("ISBTV_DEVICE_NAME", "Chromecast").strip() or "Chromecast",
            "offset": number("ISBTV_DEVICE_OFFSET", "0"),
        }
    ],
    "skip_categories": categories,
    "skip_count_tracking": flag("ISBTV_SKIP_COUNT_TRACKING", "true"),
    "mute_ads": flag("ISBTV_MUTE_ADS", "true"),
    "skip_ads": flag("ISBTV_SKIP_ADS", "true"),
    "minimum_skip_length": number("ISBTV_MIN_SKIP_LENGTH", "1"),
    "auto_play": flag("ISBTV_AUTO_PLAY", "true"),
    "join_name": "iSponsorBlockTV",
    "apikey": apikey,
    "channel_whitelist": [{"id": channel} for channel in whitelist],
    "sponsorblock_api_url": os.environ.get(
        "ISBTV_SPONSORBLOCK_API_URL", "https://sponsor.ajay.app/api/"
    ).strip(),
    "use_proxy": False,
}

CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
CONFIG_PATH.write_text(json.dumps(config, indent=4) + "\n")
print(f"wrote {CONFIG_PATH}: device={config['devices'][0]['name']!r} categories={categories}")
