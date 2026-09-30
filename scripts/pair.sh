#!/usr/bin/env sh
# One-off pairing: links this service to the YouTube app on the TV and prints the screen id
# to copy into ISBTV_SCREEN_ID in the Pi's .env.
#
# On the TV first: YouTube app -> Settings -> "Link with TV code".
set -eu

IMAGE="ghcr.io/dmunozv04/isponsorblocktv:v2.11.0"
DATA_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)/.isbtv-setup"

mkdir -p "$DATA_DIR"
docker run --rm -it -v "$DATA_DIR:/app/data" "$IMAGE" --setup-cli

echo
echo "Generated config ($DATA_DIR/config.json):"
cat "$DATA_DIR/config.json"
echo
echo "Copy the screen_id above into ISBTV_SCREEN_ID in the Pi's .env, then redeploy."
