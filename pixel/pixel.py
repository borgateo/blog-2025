#!/usr/bin/env python3
"""Privacy-friendly page view counter for borgateo.com.

Two HTTP listeners, standard library only:

- pixel (PIXEL_HOST:PIXEL_PORT, default 127.0.0.1:5009): receives `/p` hits.
  Exposed to the internet only through Tailscale Funnel + Netlify proxy.
- stats (STATS_HOST:STATS_PORT, default 127.0.0.1:5010): read-only HTML report.
  Bind it to the Tailscale IP so it stays private.

What is stored per hit: UTC time, path, referring domain, browser family,
device class, bot flag, new/is_return flag, owner flag, truncated IP
(`151.38.12.x`), country and ASN. The full IP is never written anywhere.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import ipaddress
import json
import os
import re
import sqlite3
import sys
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I drops the script dir
import geo  # noqa: E402

DATA_DIR = Path(os.environ.get("PIXEL_DATA_DIR", Path(__file__).resolve().parent / "data"))
DB_PATH = DATA_DIR / "pixel.sqlite3"
GEO_PATH = DATA_DIR / "geo.sqlite3"
SITE_HOSTS = {h.strip() for h in os.environ.get("PIXEL_SITE_HOSTS", "borgateo.com,www.borgateo.com").split(",") if h.strip()}
RETENTION_DAYS = int(os.environ.get("PIXEL_RETENTION_DAYS", "395"))  # 13 months
RATE_PER_NET = int(os.environ.get("PIXEL_RATE_PER_NET", "30"))     # hits per minute per truncated IP
RATE_GLOBAL = int(os.environ.get("PIXEL_RATE_GLOBAL", "300"))      # hits per minute in total
MAX_DB_BYTES = int(os.environ.get("PIXEL_MAX_DB_MB", "512")) * 1024 * 1024
# Only count hits that came through the Netlify proxy (direct calls to the Funnel URL are dropped).
NETLIFY_SITE_ID = os.environ.get("PIXEL_NETLIFY_SITE_ID", "")

GIF = bytes.fromhex("47494638396101000100800000000000ffffff21f90401000000002c00000000010001000002024401003b")

BOT_RE = re.compile(r"bot|crawl|spider|slurp|preview|fetch|monitor|curl|wget|python|httpx|go-http|java/|headless|lighthouse|pingdom|uptime", re.I)

SCHEMA = """
CREATE TABLE IF NOT EXISTS hits (
    id        INTEGER PRIMARY KEY,
    ts        TEXT NOT NULL,          -- UTC ISO 8601
    day       TEXT NOT NULL,          -- YYYY-MM-DD (UTC)
    path      TEXT NOT NULL,
    referrer  TEXT,                   -- domain only
    browser   TEXT,
    device    TEXT,                   -- mobile | desktop | tablet
    is_bot    INTEGER NOT NULL DEFAULT 0,
    is_return INTEGER NOT NULL DEFAULT 0,
    is_owner  INTEGER NOT NULL DEFAULT 0,
    ip_trunc  TEXT,                   -- e.g. 151.38.12.x
    country   TEXT,
    asn       INTEGER,
    as_org    TEXT
);
CREATE INDEX IF NOT EXISTS hits_day ON hits(day);
CREATE TABLE IF NOT EXISTS daily_totals (
    day       TEXT NOT NULL,
    path      TEXT NOT NULL,
    views     INTEGER NOT NULL,
    owner_views INTEGER NOT NULL,
    PRIMARY KEY (day, path)
);
"""

_db_lock = threading.Lock()


class RateLimiter:
    """Fixed one-minute windows: a per-network budget and a global one."""

    def __init__(self, per_key: int, total: int, window: float = 60.0, clock=None):
        import time
        self.per_key, self.total, self.window = per_key, total, window
        self.clock = clock or time.monotonic
        self._lock = threading.Lock()
        self._start = self.clock()
        self._counts: dict[str, int] = {}
        self._total = 0

    def allow(self, key: str) -> bool:
        with self._lock:
            now = self.clock()
            if now - self._start >= self.window:
                self._start, self._counts, self._total = now, {}, 0
            if self._total >= self.total or self._counts.get(key, 0) >= self.per_key:
                return False
            self._counts[key] = self._counts.get(key, 0) + 1
            self._total += 1
            return True


limiter = RateLimiter(RATE_PER_NET, RATE_GLOBAL)


def db_too_big() -> bool:
    try:
        return DB_PATH.stat().st_size > MAX_DB_BYTES
    except FileNotFoundError:
        return False


def db() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(SCHEMA)
    return conn


# ---------------------------------------------------------------- sanitizing

def truncate_ip(raw: str | None) -> str | None:
    """151.38.12.47 -> 151.38.12.x ; 2001:db8:85a3:8d3:1319:8a2e:370:7348 -> 2001:db8:85a3:x"""
    if not raw:
        return None
    try:
        ip = ipaddress.ip_address(raw.strip())
    except ValueError:
        return None
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
        ip = ip.ipv4_mapped
    if ip.version == 4:
        a, b, c, _ = str(ip).split(".")
        return f"{a}.{b}.{c}.x"
    groups = ip.exploded.split(":")[:3]
    return ":".join(g.lstrip("0") or "0" for g in groups) + ":x"


def geo_key(ip_trunc: str | None) -> str | None:
    """Address used for the geo lookup: the truncated IP with the hidden part set to zero."""
    if not ip_trunc:
        return None
    if "." in ip_trunc:
        return ip_trunc[:-1] + "0"
    return ip_trunc[:-1] + ":"  # 2001:db8:85a3:x -> 2001:db8:85a3::


def clean_path(raw: str | None) -> str | None:
    if not raw:
        return None
    path = urllib.parse.unquote(raw.strip())[:200]
    if not path.startswith("/") or any(ch in path for ch in "<>\"'\\ \t\r\n"):
        return None
    return path.split("?", 1)[0].split("#", 1)[0] or "/"


def clean_referrer(raw: str | None) -> str | None:
    if not raw:
        return None
    host = raw.strip().lower()
    if "//" in host:
        host = urllib.parse.urlsplit(host).hostname or ""
    host = host.split(":", 1)[0][:100]
    if not re.fullmatch(r"[a-z0-9.-]+\.[a-z]{2,}", host or ""):
        return None
    if host in SITE_HOSTS:
        return None
    return host[4:] if host.startswith("www.") else host


def classify_ua(ua: str | None) -> tuple[str, str, int]:
    ua = ua or ""
    is_bot = 1 if (not ua or BOT_RE.search(ua)) else 0
    if "Edg/" in ua:
        browser = "Edge"
    elif "OPR/" in ua or "Opera" in ua:
        browser = "Opera"
    elif "DuckDuckGo/" in ua or "Ddg/" in ua:
        browser = "DuckDuckGo"
    elif "Firefox/" in ua or "FxiOS/" in ua:
        browser = "Firefox"
    elif "SamsungBrowser/" in ua:
        browser = "Samsung"
    elif "Chrome/" in ua or "CriOS/" in ua:
        browser = "Chrome"
    elif "Safari/" in ua:
        browser = "Safari"
    else:
        browser = "Other"
    if re.search(r"iPad|Tablet", ua):
        device = "tablet"
    elif re.search(r"Mobi|iPhone|Android", ua):
        device = "mobile"
    else:
        device = "desktop"
    return browser, device, is_bot


def client_ip(headers) -> str | None:
    """Netlify sets x-nf-client-connection-ip; X-Forwarded-For is the fallback."""
    ip = headers.get("x-nf-client-connection-ip")
    if ip:
        return ip
    xff = headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return None


def record(params: dict[str, str], headers, geo_db: geo.GeoDB | None) -> bool:
    path = clean_path(params.get("p"))
    if not path:
        return False
    if NETLIFY_SITE_ID and headers.get("x-nf-site-id") != NETLIFY_SITE_ID:
        return False
    if headers.get("dnt") == "1" or headers.get("sec-gpc") == "1":
        return False
    ip_trunc = truncate_ip(client_ip(headers))
    if not limiter.allow(ip_trunc or "unknown") or db_too_big():
        return False
    browser, device, is_bot = classify_ua(headers.get("user-agent"))
    country = asn = as_org = None
    if geo_db and ip_trunc:
        country, asn, as_org = geo_db.lookup(geo_key(ip_trunc))
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    row = (
        now.isoformat().replace("+00:00", "Z"), now.date().isoformat(), path,
        clean_referrer(params.get("r")), browser, device, is_bot,
        1 if params.get("v") == "1" else 0, 1 if params.get("o") == "1" else 0,
        ip_trunc, country, asn, as_org,
    )
    with _db_lock, db() as conn:
        conn.execute(
            "INSERT INTO hits (ts, day, path, referrer, browser, device, is_bot, is_return, is_owner, ip_trunc, country, asn, as_org)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", row)
    return True


# ---------------------------------------------------------------- retention

def apply_retention(conn: sqlite3.Connection, today: dt.date | None = None) -> int:
    """Roll hits older than RETENTION_DAYS into daily_totals, then delete them."""
    today = today or dt.datetime.now(dt.timezone.utc).date()
    cutoff = (today - dt.timedelta(days=RETENTION_DAYS)).isoformat()
    conn.execute(
        "INSERT INTO daily_totals (day, path, views, owner_views)"
        " SELECT day, path, SUM(is_owner = 0), SUM(is_owner = 1) FROM hits"
        " WHERE day < ? AND is_bot = 0 GROUP BY day, path"
        " ON CONFLICT(day, path) DO UPDATE SET views = views + excluded.views, owner_views = owner_views + excluded.owner_views",
        (cutoff,))
    cur = conn.execute("DELETE FROM hits WHERE day < ?", (cutoff,))
    return cur.rowcount


# ---------------------------------------------------------------- stats page

def _table(title: str, rows, headers: list[str]) -> str:
    body = "".join("<tr>" + "".join(f"<td>{html.escape(str(c if c is not None else '—'))}</td>" for c in r) + "</tr>" for r in rows)
    head = "".join(f"<th>{html.escape(h)}</th>" for h in headers)
    return f"<section><h2>{html.escape(title)}</h2><table><thead><tr>{head}</tr></thead><tbody>{body or '<tr><td colspan=9>Nessun dato</td></tr>'}</tbody></table></section>"


def stats_html(days: int = 30, include_owner: bool = False) -> str:
    since = (dt.datetime.now(dt.timezone.utc).date() - dt.timedelta(days=days - 1)).isoformat()
    who = "" if include_owner else " AND is_owner = 0"
    base = f"FROM hits WHERE is_bot = 0 AND day >= ?{who}"
    with db() as conn:
        q = lambda sql: conn.execute(sql, (since,)).fetchall()  # noqa: E731
        total, new, ret = q(f"SELECT COUNT(*), SUM(is_return = 0), SUM(is_return = 1) {base}")[0]
        owner = conn.execute("SELECT COUNT(*) FROM hits WHERE is_bot = 0 AND is_owner = 1 AND day >= ?", (since,)).fetchone()[0]
        bots = conn.execute("SELECT COUNT(*) FROM hits WHERE is_bot = 1 AND day >= ?", (since,)).fetchone()[0]
        per_day = q(f"SELECT day, COUNT(*), SUM(is_return = 0) {base} GROUP BY day ORDER BY day DESC")
        pages = q(f"SELECT path, COUNT(*) {base} GROUP BY path ORDER BY 2 DESC LIMIT 20")
        refs = q(f"SELECT COALESCE(referrer, '(diretto)'), COUNT(*) {base} GROUP BY 1 ORDER BY 2 DESC LIMIT 15")
        countries = q(f"SELECT COALESCE(country, '?'), COUNT(*) {base} GROUP BY 1 ORDER BY 2 DESC LIMIT 15")
        nets = q(f"SELECT COALESCE(as_org, '?'), COUNT(*) {base} GROUP BY 1 ORDER BY 2 DESC LIMIT 10")
        browsers = q(f"SELECT browser || ' · ' || device, COUNT(*) {base} GROUP BY 1 ORDER BY 2 DESC LIMIT 10")
        recent = conn.execute(
            "SELECT substr(ts, 1, 16), path, COALESCE(referrer, ''), country, ip_trunc, browser, device,"
            " CASE WHEN is_return THEN 'ritorno' ELSE 'nuovo' END, CASE WHEN is_owner THEN 'io' ELSE '' END"
            " FROM hits WHERE is_bot = 0 ORDER BY id DESC LIMIT 25").fetchall()
    toggle = (f'<a href="?days={days}">nascondi le mie visite</a>' if include_owner
              else f'<a href="?days={days}&amp;io=1">includi le mie visite</a>')
    ranges = " · ".join(f'<a href="?days={d}{"&amp;io=1" if include_owner else ""}">{d} giorni</a>' for d in (7, 30, 90, 395))
    owner_note = "incluse" if include_owner else f"escluse ({owner})"
    return f"""<!doctype html><html lang="it"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>borgateo.com · visite</title>
<style>
:root{{color-scheme:light dark;--bg:#fff;--fg:#1f2430;--muted:#6b7280;--line:#e5e7eb;--accent:#b7791f}}
@media (prefers-color-scheme:dark){{:root{{--bg:#1f2430;--fg:#cbccc6;--muted:#8a8f98;--line:#343b4a;--accent:#ffcc66}}}}
body{{font:15px/1.45 system-ui,sans-serif;background:var(--bg);color:var(--fg);max-width:960px;margin:0 auto;padding:16px}}
a{{color:var(--accent)}} h1{{margin:.2em 0}} h2{{font-size:1rem;margin:1.6em 0 .4em}}
.kpi{{display:flex;flex-wrap:wrap;gap:12px;margin:12px 0}} .kpi div{{border:1px solid var(--line);border-radius:8px;padding:8px 12px}}
.kpi b{{display:block;font-size:1.4rem}} .muted{{color:var(--muted)}}
table{{border-collapse:collapse;width:100%;font-size:.9rem}} td,th{{text-align:left;padding:4px 8px;border-bottom:1px solid var(--line);white-space:nowrap}}
section{{overflow-x:auto}}
</style>
<h1>borgateo.com · visite</h1>
<p class="muted">Ultimi {days} giorni · {ranges}<br>Le mie visite: {owner_note} · {toggle} · bot scartati: {bots}</p>
<div class="kpi"><div><b>{total or 0}</b>visite</div><div><b>{new or 0}</b>nuovi</div><div><b>{ret or 0}</b>di ritorno</div></div>
{_table("Per giorno", per_day, ["Giorno", "Visite", "Nuovi"])}
{_table("Pagine", pages, ["Pagina", "Visite"])}
{_table("Provenienza", refs, ["Sito", "Visite"])}
{_table("Paesi", countries, ["Paese", "Visite"])}
{_table("Provider", nets, ["Provider", "Visite"])}
{_table("Browser", browsers, ["Browser", "Visite"])}
{_table("Ultime 25 visite (tutte, anche le mie)", recent, ["Quando (UTC)", "Pagina", "Da", "Paese", "IP", "Browser", "Dispositivo", "Tipo", ""])}
<p class="muted">Geolocalizzazione: <a href="https://db-ip.com">IP Geolocation by DB-IP</a> (CC BY 4.0).</p>
</html>"""


# ---------------------------------------------------------------- HTTP

class PixelHandler(BaseHTTPRequestHandler):
    server_version = "pixel"
    sys_version = ""
    timeout = 10  # drop slow or idle connections instead of holding a thread
    geo_db: geo.GeoDB | None = None

    def log_message(self, *args):  # no access log: it would contain full IPs
        pass

    def _hit(self, body: bool):
        url = urllib.parse.urlsplit(self.path)
        if url.path.rstrip("/") != "/p":
            self.send_response(404)
            self.end_headers()
            return
        params = {k: v[0] for k, v in urllib.parse.parse_qs(url.query).items()}
        try:
            record(params, self.headers, self.geo_db)
        except Exception as exc:  # never break the page for a counter
            print(f"record failed: {exc!r}", file=sys.stderr)
        self.send_response(200 if body else 204)
        self.send_header("Cache-Control", "no-store")
        if body:
            self.send_header("Content-Type", "image/gif")
            self.send_header("Content-Length", str(len(GIF)))
        self.end_headers()
        if body:
            self.wfile.write(GIF)

    def do_GET(self):
        self._hit(body=True)

    def do_POST(self):
        length = min(int(self.headers.get("content-length") or 0), 1024)
        if length:
            self.rfile.read(length)
        self._hit(body=False)


class StatsHandler(BaseHTTPRequestHandler):
    server_version = "pixel-stats"
    sys_version = ""
    timeout = 10

    def log_message(self, *args):
        pass

    def do_GET(self):
        url = urllib.parse.urlsplit(self.path)
        q = urllib.parse.parse_qs(url.query)
        if url.path == "/api/summary":
            payload = summary_json()
            data = json.dumps(payload).encode()
            ctype = "application/json"
        elif url.path == "/":
            try:
                days = max(1, min(int(q.get("days", ["30"])[0]), 3650))
            except ValueError:
                days = 30
            data = stats_html(days, include_owner=q.get("io", ["0"])[0] == "1").encode()
            ctype = "text/html; charset=utf-8"
        else:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def summary_json() -> dict:
    """Small summary, handy for a future weekly Telegram report."""
    today = dt.datetime.now(dt.timezone.utc).date()
    since = (today - dt.timedelta(days=6)).isoformat()
    with db() as conn:
        total, new = conn.execute(
            "SELECT COUNT(*), SUM(is_return = 0) FROM hits WHERE is_bot = 0 AND is_owner = 0 AND day >= ?", (since,)).fetchone()
        top = conn.execute(
            "SELECT path, COUNT(*) FROM hits WHERE is_bot = 0 AND is_owner = 0 AND day >= ? GROUP BY path ORDER BY 2 DESC LIMIT 5",
            (since,)).fetchall()
    return {"since": since, "views": total or 0, "new": new or 0, "top": top}


def serve():
    geo_db = geo.GeoDB(GEO_PATH) if GEO_PATH.exists() else None
    if geo_db is None:
        print(f"geo database missing at {GEO_PATH}: country/ASN disabled", file=sys.stderr)
    PixelHandler.geo_db = geo_db
    with db() as conn:
        removed = apply_retention(conn)
    print(f"retention: removed {removed} old hits", file=sys.stderr)
    pixel = ThreadingHTTPServer((os.environ.get("PIXEL_HOST", "127.0.0.1"), int(os.environ.get("PIXEL_PORT", "5009"))), PixelHandler)
    stats = ThreadingHTTPServer((os.environ.get("STATS_HOST", "127.0.0.1"), int(os.environ.get("STATS_PORT", "5010"))), StatsHandler)
    threading.Thread(target=stats.serve_forever, daemon=True).start()
    print(f"pixel on {pixel.server_address}, stats on {stats.server_address}", file=sys.stderr)
    pixel.serve_forever()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("serve", help="run the pixel and stats servers")
    sub.add_parser("retention", help="roll up and delete hits older than 13 months")
    g = sub.add_parser("build-geo", help="build the geo database from DB-IP Lite CSV files")
    g.add_argument("country_csv_gz")
    g.add_argument("asn_csv_gz")
    args = ap.parse_args(argv)
    if args.cmd == "serve":
        serve()
    elif args.cmd == "retention":
        with db() as conn:
            print(f"removed {apply_retention(conn)} hits")
    elif args.cmd == "build-geo":
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        n = geo.build(Path(args.country_csv_gz), Path(args.asn_csv_gz), GEO_PATH)
        print(f"geo database ready: {n} ranges")


if __name__ == "__main__":
    main()
