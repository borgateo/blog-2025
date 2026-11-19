# Page view pixel

A tiny, first-party page view counter for borgateo.com. No cookies, no third-party scripts, no full IP addresses.
The public explanation for readers lives at [/privacy/](../src/privacy.md).

## How it works

```
browser ── POST /p?... ──▶ Netlify (borgateo.com) ──proxy──▶ Tailscale Funnel ──▶ RPi 127.0.0.1:5009
                                                                                    │
                                                         SQLite (/mnt/nas/services/blog-pixel/data)
                                                                                    │
                                              stats page on Tailscale only ◀── RPi 100.79.128.60:5010
```

1. `src/_includes/partials/pixel.html` runs after the page has loaded (`requestIdleCallback`) and sends one `navigator.sendBeacon` to `/p`. It sends nothing if the browser has Do Not Track or Global Privacy Control on, and only runs on `borgateo.com`.
2. `netlify.toml` proxies `/p` to the Raspberry Pi through Tailscale Funnel, so the request stays first-party and the tailnet name never appears in the page.
3. `pixel.py serve` stores one row per hit and answers `204` (or a 1×1 GIF for `GET`). Hits over the rate limit are answered the same way but not stored.

### What is stored

| Column | Example | Notes |
|---|---|---|
| `ts`, `day` | `2026-11-19T13:25:00Z` | UTC |
| `path` | `/posts/chi-accende-la-luce/` | query string and fragment dropped |
| `referrer` | `google.com` | domain only, own domain dropped |
| `browser`, `device` | `Safari`, `mobile` | from `User-Agent`, which is not stored |
| `is_bot` | `0` | bots are kept but hidden from the stats |
| `is_return` | `1` | from the `bg_seen` flag in `localStorage` (no ID, resets after 13 months) |
| `is_owner` | `1` | my own visits, see below |
| `ip_trunc` | `151.38.12.x`, `2001:db8:85a3:x` | IPv4 keeps 3 of 4 parts, IPv6 keeps 3 of 8 groups |
| `country`, `asn`, `as_org` | `IT`, `1267`, `WIND TRE S.P.A.` | looked up from the truncated IP |

The full IP is never written: there is no access log (`log_message` is a no-op) and only the truncated form reaches SQLite. Netlify sets `x-nf-client-connection-ip`, with `X-Forwarded-For` as fallback.

### My own visits

Open any page with `?io` once on each of my devices (e.g. `https://borgateo.com/?io`). The browser stores `bg_me=1` and every later hit is tagged `is_owner=1`. They are kept, labelled `io` in the stats and excluded from the totals unless the page is opened with `&io=1`.

### Retention

Rows older than 395 days (13 months) are rolled up into `daily_totals` (views per day and page) and deleted. This runs at startup and daily at 04:20 via `blog-pixel-maintenance.timer`. 13 months follows the CNIL guidance for consent-exempt audience measurement, and leaves room to compare a month with the same month a year earlier.

### Geolocation

[DB-IP Lite](https://db-ip.com/db/lite.php) country and ASN CSVs (CC BY 4.0, attribution on the privacy page and the stats page), converted into `geo.sqlite3` (~160 MB). The maintenance job refreshes it when it is older than 32 days.

## Stats

`http://100.79.128.60:5010/` (Tailscale only), linked from the Lab 307 dashboard. Query parameters: `days=7|30|90|395`, `io=1` to include my visits. `GET /api/summary` returns the last 7 days as JSON and `GET /health` returns `{"ok": true}`; both send `Access-Control-Allow-Origin` for the dashboard origin only (`PIXEL_DASHBOARD_ORIGIN`).

## Security

This is the only service of the Raspberry Pi reachable from the internet, so it is locked down:

- **Only `/p` is public**: Tailscale Funnel forwards that path to `127.0.0.1:5009`. No router port is open and the home IP stays hidden.
- **Dedicated user** `blog-pixel` (system account, no shell, no home), not the main user that has passwordless `sudo`.
- **Filesystem**: code in `/opt/blog-pixel` owned by root and read-only; `ProtectSystem=strict`, `ProtectHome=yes`; the only writable path is the data dir (mode 700).
- **No privileges**: `NoNewPrivileges`, empty capability set, `SystemCallFilter=@system-service`, plus the usual `Protect*`/`Restrict*` options.
- **Network**: `IPAddressDeny=any`, allowed only loopback and the tailnet (`100.64.0.0/10`, `fd7a:115c:a1e0::/48`). No LAN, no internet. The maintenance unit can reach the internet to download DB-IP.
- **Netlify only**: hits without Netlify's `x-nf-site-id` for this site are dropped, so calling the Funnel URL directly (it is listed in public certificate logs) counts nothing.
- **Abuse**: 30 hits/min per truncated IP, 300/min in total, database capped at 512 MB, 10 s socket timeout, `MemoryMax=256M`, `CPUQuota=25%`, `TasksMax=64`.
- **Stats page**: bound to the Tailscale IP only, every value escaped with `html.escape`.

Checked on 2026-11-19: `systemd-analyze security blog-pixel` scores **1.2 OK**; with the same restrictions the home, `sudo`, `/opt`, the LAN router and the internet are unreachable while the tailnet works; 40 hits from one network store 30.

Known residual risk: `http.server` is not meant for public production use. A bug there would stay confined to the pixel's data dir.

## Deploy (Raspberry Pi)

```sh
# on the Mac, from this folder: copy to a staging dir
rsync -a --delete --exclude data --exclude __pycache__ --exclude test_pixel.py --exclude .gitignore ./ borgateo@100.79.128.60:/home/borgateo/blog-pixel/

# on the RPi, first time only
sudo useradd --system --no-create-home --home-dir /nonexistent --shell /usr/sbin/nologin blog-pixel
sudo mkdir -p /mnt/nas/services/blog-pixel/data
sudo chown blog-pixel:blog-pixel /mnt/nas/services/blog-pixel/data && sudo chmod 700 /mnt/nas/services/blog-pixel/data

# on the RPi, every deploy
sudo rsync -a --delete --chown=root:root /home/borgateo/blog-pixel/ /opt/blog-pixel/ && rm -rf /home/borgateo/blog-pixel
sudo cp /opt/blog-pixel/deploy/*.service /opt/blog-pixel/deploy/*.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start blog-pixel-maintenance.service      # first time: builds geo.sqlite3
sudo systemctl enable --now blog-pixel.service blog-pixel-maintenance.timer
sudo systemctl restart blog-pixel.service

# expose only /p (first time; Funnel must be enabled for the tailnet)
sudo tailscale funnel --bg --set-path /p http://127.0.0.1:5009/p
```

## Tests

```sh
python3 -m unittest test_pixel
```

## Ideas for later

- **Weekly Telegram summary**: the bot could call `GET /api/summary` every Monday and send views, new visitors and top pages. Not worth it while traffic is this low.
