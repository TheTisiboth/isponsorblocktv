# iSponsorBlockTV 📺

Skips YouTube **sponsor segments** and mutes/skips **YouTube ads** on the Chromecast with
Google TV, using the [SponsorBlock](https://sponsor.ajay.app/) database.

Runs [iSponsorBlockTV](https://github.com/dmunozv04/iSponsorBlockTV) on the Pi as part of the
[Pi5 stack](https://github.com/TheTisiboth/raspberry-pi-config). No web UI.

## How it works

SponsorBlock is a segment *database* plus a *client* that does the seeking. On a TV there is no
browser extension, so this service plays the role of the client:

1. Paired once with the TV's YouTube app via a **TV link code**, which yields a `screen_id`.
2. With that token it joins the TV's session over YouTube's **Lounge API** — the same protocol
   your phone uses as a cast remote.
3. While a video plays it queries SponsorBlock and tells the TV to seek past sponsor segments,
   and mutes/skips YouTube's own ads.

Videos **cast** to the device are covered too: the TV's own YouTube app is what plays them.

Both the TV and this container talk to Google's servers, never to each other — so the service
needs nothing but **outbound access to youtube.com**: no host networking, no LAN discovery, no
published port. (Auto-discovery, the only feature that needs `network_mode: host`, is
deliberately unused; it was also the source of CVE-2026-77597.)

**Laptops need nothing from this repo** — install the SponsorBlock browser extension instead.

## Setup

### 1. Pair the TV (once)

On the TV: **YouTube app → Settings → Link with TV code**. Then, from a machine with Docker:

```sh
scripts/pair.sh
```

Enter the code; the script prints the generated config, including the `screen_id`.

### 2. Configure

Copy `.env.example` to `.env` and set `ISBTV_SCREEN_ID` to that value. Everything else is
optional — see the comments in `.env.example`.

`config.json` is **not** committed or hand-written: a `config-init` container renders it from
`.env` on every start, so `.env` is the single source of truth and the pairing token (which is a
remote control for that YouTube app) stays out of git.

### 3. Deploy

Dokploy → new **Compose** application → this repo, branch `main`, Compose Path
`docker-compose.yml`, paste the `.env`, Deploy. Later pushes redeploy automatically.

> There is no `docker-compose.prod.yml` here, unlike the other stack repos: the service is not
> Traefik-routed and is not probed over `dokploy-network` (homepage gets its status dot from the
> Docker socket), so a prod overlay would have nothing to attach.

## Operating it

```sh
docker compose logs -f isponsorblocktv
```

- `Segment skipped` / ad lines confirm it is driving the TV.
- `Refresh auth failed` on a loop means the `screen_id` is no longer valid. YouTube rotates
  screen ids occasionally: re-run `scripts/pair.sh`, update `ISBTV_SCREEN_ID` in `.env`, redeploy.
- Changing what gets skipped is an `.env` edit plus a redeploy (`ISBTV_SKIP_CATEGORIES`).
- `ISBTV_CHANNEL_WHITELIST` requires `ISBTV_APIKEY` (a YouTube Data API key); `config-init`
  refuses to render a config that would crash the app.

## Defaults

| Setting | Value |
|---|---|
| Skipped categories | `sponsor` |
| YouTube ads | muted **and** skipped |
| Minimum segment length | 1s |
| Autoplay | left enabled |
| Skip-count tracking | on (anonymous ping to sponsor.ajay.app) |
| Channel whitelist | empty |
