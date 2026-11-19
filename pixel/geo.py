"""Country and ASN lookup from DB-IP Lite CSV files (CC BY 4.0, https://db-ip.com).

The CSVs are converted once into a small SQLite database with one range table
per family: IPv4 ranges as integers, IPv6 ranges as 32-char hex strings, so a
lookup is a single indexed query.
"""

from __future__ import annotations

import csv
import gzip
import io
import ipaddress
import os
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE country (fam INTEGER, start TEXT, stop TEXT, cc TEXT);
CREATE TABLE asn (fam INTEGER, start TEXT, stop TEXT, num INTEGER, org TEXT);
"""


def _key(ip: ipaddress._BaseAddress) -> str:
    # fixed-width hex keeps lexical order equal to numeric order for both families
    return format(int(ip), "032x")


def _rows(path: Path):
    with gzip.open(path, "rb") as raw:
        for row in csv.reader(io.TextIOWrapper(raw, encoding="utf-8", newline="")):
            if len(row) < 3:
                continue
            try:
                a, b = ipaddress.ip_address(row[0]), ipaddress.ip_address(row[1])
            except ValueError:
                continue
            yield a.version, _key(a), _key(b), row[2:]


def build(country_csv: Path, asn_csv: Path, out: Path) -> int:
    tmp = out.with_suffix(".tmp")
    if tmp.exists():
        tmp.unlink()
    conn = sqlite3.connect(tmp)
    conn.executescript(SCHEMA)
    n = 0
    batch = []
    for fam, a, b, rest in _rows(country_csv):
        batch.append((fam, a, b, rest[0][:2]))
        if len(batch) >= 50000:
            conn.executemany("INSERT INTO country VALUES (?,?,?,?)", batch)
            n += len(batch)
            batch.clear()
    conn.executemany("INSERT INTO country VALUES (?,?,?,?)", batch)
    n += len(batch)
    batch = []
    for fam, a, b, rest in _rows(asn_csv):
        try:
            num = int(rest[0])
        except (ValueError, IndexError):
            continue
        batch.append((fam, a, b, num, (rest[1] if len(rest) > 1 else "")[:120]))
        if len(batch) >= 50000:
            conn.executemany("INSERT INTO asn VALUES (?,?,?,?,?)", batch)
            n += len(batch)
            batch.clear()
    conn.executemany("INSERT INTO asn VALUES (?,?,?,?,?)", batch)
    n += len(batch)
    conn.execute("CREATE INDEX country_start ON country(fam, start)")
    conn.execute("CREATE INDEX asn_start ON asn(fam, start)")
    conn.commit()
    conn.execute("VACUUM")
    conn.close()
    os.replace(tmp, out)
    return n


class GeoDB:
    def __init__(self, path: Path):
        self.path = path

    def lookup(self, ip_text: str | None) -> tuple[str | None, int | None, str | None]:
        if not ip_text:
            return None, None, None
        try:
            ip = ipaddress.ip_address(ip_text)
        except ValueError:
            return None, None, None
        key, fam = _key(ip), ip.version
        conn = sqlite3.connect(f"file:{self.path}?mode=ro", uri=True)
        try:
            c = conn.execute(
                "SELECT cc, stop FROM country WHERE fam = ? AND start <= ? ORDER BY start DESC LIMIT 1", (fam, key)).fetchone()
            a = conn.execute(
                "SELECT num, org, stop FROM asn WHERE fam = ? AND start <= ? ORDER BY start DESC LIMIT 1", (fam, key)).fetchone()
        finally:
            conn.close()
        cc = c[0] if c and c[1] >= key and c[0] != "ZZ" else None
        num, org = (a[0], a[1]) if a and a[2] >= key else (None, None)
        return cc, num, org
