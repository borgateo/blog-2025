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
DASHBOARD_ORIGIN = os.environ.get("PIXEL_DASHBOARD_ORIGIN", "http://100.79.128.60:5000")

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

def _flag(cc: str | None) -> str:
    if not cc or len(cc) != 2 or not cc.isalpha():
        return "🏳️"
    return "".join(chr(0x1F1E6 + ord(c) - ord("A")) for c in cc.upper())


def _ranked(title: str, rows, label=lambda v: html.escape(str(v)), empty="Ancora niente") -> str:
    rows = list(rows)
    if not rows:
        body = f'<p class="empty">{empty}</p>'
    else:
        top = max(r[1] for r in rows) or 1
        body = "<ol class=\"rank\">" + "".join(
            f'<li><span class="bar" style="--w:{max(2, round(100 * n / top))}%"></span>'
            f'<span class="rk-label">{label(v)}</span><span class="rk-val">{n}</span></li>'
            for v, n in rows) + "</ol>"
    return f'<section class="card"><h2>{html.escape(title)}</h2>{body}</section>'


def stats_html(days: int = 30, include_owner: bool = False) -> str:
    today = dt.datetime.now(dt.timezone.utc).date()
    since = (today - dt.timedelta(days=days - 1)).isoformat()
    who = "" if include_owner else " AND is_owner = 0"
    base = f"FROM hits WHERE is_bot = 0 AND day >= ?{who}"
    with db() as conn:
        q = lambda sql: conn.execute(sql, (since,)).fetchall()  # noqa: E731
        total, new, ret = q(f"SELECT COUNT(*), SUM(is_return = 0), SUM(is_return = 1) {base}")[0]
        owner = conn.execute("SELECT COUNT(*) FROM hits WHERE is_bot = 0 AND is_owner = 1 AND day >= ?", (since,)).fetchone()[0]
        bots = conn.execute("SELECT COUNT(*) FROM hits WHERE is_bot = 1 AND day >= ?", (since,)).fetchone()[0]
        per_day = {d: (n, nw) for d, n, nw in q(f"SELECT day, COUNT(*), SUM(is_return = 0) {base} GROUP BY day")}
        pages = q(f"SELECT path, COUNT(*) {base} GROUP BY path ORDER BY 2 DESC LIMIT 12")
        refs = q(f"SELECT COALESCE(referrer, 'diretto'), COUNT(*) {base} GROUP BY 1 ORDER BY 2 DESC LIMIT 10")
        countries = q(f"SELECT country, COUNT(*) {base} GROUP BY 1 ORDER BY 2 DESC LIMIT 10")
        nets = q(f"SELECT COALESCE(as_org, '?'), COUNT(*) {base} GROUP BY 1 ORDER BY 2 DESC LIMIT 8")
        browsers = q(f"SELECT browser || ' · ' || device, COUNT(*) {base} GROUP BY 1 ORDER BY 2 DESC LIMIT 8")
        recent = conn.execute(
            "SELECT ts, path, referrer, country, ip_trunc, browser, device, is_return, is_owner"
            " FROM hits WHERE is_bot = 0 ORDER BY id DESC LIMIT 25").fetchall()
    series = []
    for i in range(days):
        d = (today - dt.timedelta(days=days - 1 - i)).isoformat()
        n, nw = per_day.get(d, (0, 0))
        series.append({"d": d, "n": n, "new": nw or 0})
    io_q = "&amp;io=1" if include_owner else ""
    ranges = "".join(
        f'<a class="pill{" on" if d == days else ""}" href="?days={d}{io_q}">{lbl}</a>'
        for d, lbl in ((7, "7 giorni"), (30, "30 giorni"), (90, "90 giorni"), (395, "13 mesi")))
    toggle = (f'<a class="pill on" href="?days={days}">Mie visite incluse ({owner})</a>' if include_owner
              else f'<a class="pill" href="?days={days}&amp;io=1">Mie visite escluse ({owner})</a>')

    def kpi(label, value, hint=""):
        return f'<div class="kpi"><span class="kpi-label">{label}</span><span class="kpi-val">{value}</span><span class="kpi-hint">{hint}</span></div>'

    share = f"{round(100 * (ret or 0) / total)}% del totale" if total else ""
    kpis = (kpi("Visite", total or 0, f"ultimi {days} giorni")
            + kpi("Nuovi", new or 0, "primo passaggio")
            + kpi("Di ritorno", ret or 0, share)
            + kpi("Bot scartati", bots, "non contati"))

    rows = "".join(
        "<tr>"
        f"<td class=\"mono\">{html.escape(ts[5:16].replace('T', ' '))}</td>"
        f"<td class=\"path\">{html.escape(path)}</td>"
        f"<td>{html.escape(ref or '—')}</td>"
        f"<td>{_flag(cc)} {html.escape(cc or '')}</td>"
        f"<td class=\"mono\">{html.escape(ip or '—')}</td>"
        f"<td>{html.escape(br or '')} · {html.escape(dev or '')}</td>"
        f"<td><span class=\"tag {'ret' if r else 'new'}\">{'ritorno' if r else 'nuovo'}</span>"
        f"{' <span class=\"tag me\">io</span>' if o else ''}</td>"
        "</tr>" for ts, path, ref, cc, ip, br, dev, r, o in recent)
    data = json.dumps(series).replace("</", "<\\/")
    return f"""<!doctype html><html lang="it"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Visite · borgateo.com</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>📈</text></svg>">
<style>
:root{{--bg:#f4f6fb;--bg2:#e8edf7;--surface:#ffffff;--border:rgba(30,50,90,.12);--text:#14203a;--text-2:#46536b;--text-3:#6b7891;
--bar:#2f6fe0;--bar-soft:rgba(47,111,224,.14);--new:#2f6fe0;--ret:#0f8a5f;--me:#b45309;--radius:14px}}
@media (prefers-color-scheme:dark){{:root{{--bg:#0a1224;--bg2:#131e3a;--surface:rgba(20,30,56,.72);--border:rgba(120,150,200,.16);
--text:#e8edf6;--text-2:#a8b3c8;--text-3:#7d89a3;--bar:#6ea8ff;--bar-soft:rgba(110,168,255,.16);--new:#6ea8ff;--ret:#4ade80;--me:#fbbf24}}}}
*{{box-sizing:border-box}}
body{{margin:0;font:15px/1.45 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;color:var(--text);
background:radial-gradient(1200px 600px at 10% -10%,var(--bg2),transparent),var(--bg);min-height:100vh}}
.wrap{{max-width:1080px;margin:0 auto;padding:28px 16px 48px}}
header{{display:flex;flex-wrap:wrap;align-items:flex-end;justify-content:space-between;gap:12px;margin-bottom:18px}}
h1{{margin:0;font-size:1.6rem;letter-spacing:-.01em}} h1 small{{display:block;font-size:.85rem;font-weight:500;color:var(--text-3);margin-top:2px}}
a{{color:inherit}} .back{{color:var(--text-3);text-decoration:none;font-size:.85rem}} .back:hover{{color:var(--text)}}
.pills{{display:flex;flex-wrap:wrap;gap:6px}}
.pill{{padding:5px 11px;border:1px solid var(--border);border-radius:999px;text-decoration:none;font-size:.82rem;color:var(--text-2);background:var(--surface)}}
.pill.on{{color:var(--text);border-color:var(--bar);box-shadow:inset 0 0 0 1px var(--bar)}}
.kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:14px 0}}
.kpi,.card{{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);backdrop-filter:blur(6px)}}
.kpi{{padding:14px 16px;display:flex;flex-direction:column;gap:2px}}
.kpi-label{{font-size:.75rem;text-transform:uppercase;letter-spacing:.06em;color:var(--text-3)}}
.kpi-val{{font-size:1.9rem;font-weight:650;font-variant-numeric:tabular-nums}} .kpi-hint{{font-size:.8rem;color:var(--text-3)}}
.card{{padding:16px 18px;min-width:0}} .card h2{{margin:0 0 12px;font-size:.95rem;font-weight:600}}
.chart{{position:relative}} .chart svg{{display:block;overflow:visible}}
.axis{{fill:var(--text-3);font-size:11px}} .grid line{{stroke:var(--border)}}
.tip{{position:absolute;pointer-events:none;background:var(--text);color:var(--bg);padding:6px 9px;border-radius:8px;font-size:.8rem;
white-space:nowrap;transform:translate(-50%,-110%);opacity:0;transition:opacity .1s}}
.cols{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px;margin-top:12px}}
.rank{{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:6px}}
.rank li{{position:relative;display:flex;align-items:center;gap:10px;padding:5px 8px;border-radius:7px;overflow:hidden}}
.rank .bar{{position:absolute;inset:0 auto 0 0;width:var(--w);background:var(--bar-soft);border-radius:7px}}
.rk-label{{position:relative;flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.rk-val{{position:relative;font-variant-numeric:tabular-nums;color:var(--text-2)}}
.empty{{color:var(--text-3);margin:0}}
.table-wrap{{overflow-x:auto}} table{{border-collapse:collapse;width:100%;font-size:.86rem}}
th{{text-align:left;font-weight:500;color:var(--text-3);font-size:.75rem;text-transform:uppercase;letter-spacing:.05em}}
td,th{{padding:7px 8px;border-bottom:1px solid var(--border);white-space:nowrap}} tr:last-child td{{border-bottom:0}}
.mono{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.8rem;color:var(--text-2)}}
.path{{max-width:280px;overflow:hidden;text-overflow:ellipsis}}
.tag{{display:inline-block;padding:1px 7px;border-radius:999px;font-size:.72rem;border:1px solid currentColor}}
.tag.new{{color:var(--new)}} .tag.ret{{color:var(--ret)}} .tag.me{{color:var(--me)}}
footer{{margin-top:22px;color:var(--text-3);font-size:.8rem}}
@media (max-width:720px){{.kpis{{grid-template-columns:1fr 1fr}} .kpi-val{{font-size:1.5rem}}}}
</style></head><body><div class="wrap">
<a class="back" href="http://100.79.128.60:5000/">← Lab 307</a>
<header><h1>📈 Visite borgateo.com<small>Contatore fatto in casa · IP troncati · niente cookie</small></h1>
<div class="pills">{ranges}{toggle}</div></header>
<div class="kpis">{kpis}</div>
<section class="card"><h2>Visite per giorno</h2><div class="chart" id="chart"><div class="tip" id="tip"></div></div></section>
<div class="cols">
{_ranked("Pagine", pages)}
{_ranked("Da dove arrivano", refs)}
{_ranked("Paesi", countries, label=lambda c: f"{_flag(c)} {html.escape(c or 'sconosciuto')}")}
{_ranked("Provider", nets)}
{_ranked("Browser e dispositivo", browsers)}
</div>
<section class="card" style="margin-top:12px"><h2>Ultime 25 visite <span class="kpi-hint">(anche le mie, segnate <span class="tag me">io</span>)</span></h2>
<div class="table-wrap"><table><thead><tr><th>Quando (UTC)</th><th>Pagina</th><th>Da</th><th>Paese</th><th>IP</th><th>Browser</th><th>Tipo</th></tr></thead>
<tbody>{rows or '<tr><td colspan="7" class="empty">Ancora nessuna visita</td></tr>'}</tbody></table></div></section>
<footer>Dati conservati 13 mesi, poi solo totali giornalieri · Geolocalizzazione: <a href="https://db-ip.com">IP Geolocation by DB-IP</a> (CC BY 4.0) · <a href="https://borgateo.com/privacy/">pagina privacy</a></footer>
</div>
<script>
const DATA = {data};
(function () {{
  const box = document.getElementById('chart'), tip = document.getElementById('tip');
  const H = 220, L = 34, B = 24, T = 10;
  const max = Math.max(1, ...DATA.map(d => d.n));
  const raw = max / 4, mag = Math.pow(10, Math.floor(Math.log10(raw)));
  const step = Math.max(1, [1, 2, 5, 10].map(m => m * mag).find(v => v >= raw));
  const top = step * 4;
  const y = v => T + (H - T - B) * (1 - v / top);
  const fmt = d => new Date(d + 'T00:00:00Z').toLocaleDateString('it-IT', {{day: 'numeric', month: 'short', timeZone: 'UTC'}});
  function draw() {{
    const W = box.clientWidth, n = DATA.length, slot = (W - L) / n, bw = Math.max(2, Math.min(28, slot - 3));
    let s = `<svg width="${{W}}" height="${{H}}" role="img" aria-label="Visite per giorno"><g class="grid">`;
    for (let i = 0; i <= 4; i++) {{ const v = step * i, yy = y(v);
      s += `<line x1="${{L}}" x2="${{W}}" y1="${{yy}}" y2="${{yy}}"/><text class="axis" x="${{L - 8}}" y="${{yy + 4}}" text-anchor="end">${{v}}</text>`; }}
    s += '</g>';
    const every = Math.max(1, Math.ceil(n / Math.max(2, Math.floor((W - L) / 64))));
    DATA.forEach((d, i) => {{
      const x = L + i * slot + (slot - bw) / 2, h = Math.max(0, H - B - y(d.n)), r = Math.min(4, bw / 2, h);
      if (d.n > 0) s += `<path fill="var(--bar)" d="M${{x}},${{H - B}} v${{-(h - r)}} q0,${{-r}} ${{r}},${{-r}} h${{bw - 2 * r}} q${{r}},0 ${{r}},${{r}} v${{h - r}} z"/>`;
      s += `<rect data-i="${{i}}" x="${{L + i * slot}}" y="${{T}}" width="${{slot}}" height="${{H - T}}" fill="transparent"/>`;
      if ((n - 1 - i) % every === 0) s += `<text class="axis" x="${{x + bw / 2}}" y="${{H - 6}}" text-anchor="middle">${{fmt(d.d)}}</text>`;
    }});
    box.querySelector('svg')?.remove();
    box.insertAdjacentHTML('afterbegin', s + '</svg>');
    box.querySelector('svg').addEventListener('mousemove', e => {{
      const t = e.target.closest('rect[data-i]'); if (!t) {{ tip.style.opacity = 0; return; }}
      const d = DATA[+t.dataset.i], rb = box.getBoundingClientRect(), tb = t.getBoundingClientRect();
      tip.innerHTML = `<b>${{fmt(d.d)}}</b> · ${{d.n}} visite · ${{d.new}} nuovi`;
      tip.style.left = (tb.left - rb.left + tb.width / 2) + 'px'; tip.style.top = y(d.n) + 'px'; tip.style.opacity = 1;
    }});
  }}
  draw();
  let rt; addEventListener('resize', () => {{ clearTimeout(rt); rt = setTimeout(draw, 120); }});
  box.addEventListener('mouseleave', () => tip.style.opacity = 0);
}})();
</script></body></html>"""


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
        if url.path in ("/api/summary", "/health"):
            payload = summary_json() if url.path == "/api/summary" else {"ok": True}
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
        self.send_header("Cache-Control", "no-store")
        if ctype == "application/json":  # read by the Lab 307 dashboard widget
            self.send_header("Access-Control-Allow-Origin", DASHBOARD_ORIGIN)
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
