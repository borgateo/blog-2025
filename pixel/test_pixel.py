import datetime as dt
import os
import tempfile
import unittest
from pathlib import Path

os.environ["PIXEL_DATA_DIR"] = tempfile.mkdtemp(prefix="pixel-test-")

import pixel  # noqa: E402


class Headers(dict):
    def get(self, key, default=None):
        return super().get(key.lower(), default)


CHROME_MAC = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
SAFARI_IPHONE = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1"


class TruncateIp(unittest.TestCase):
    def test_ipv4(self):
        self.assertEqual(pixel.truncate_ip("151.38.12.47"), "151.38.12.x")

    def test_ipv6(self):
        self.assertEqual(pixel.truncate_ip("2001:0db8:85a3:08d3:1319:8a2e:0370:7348"), "2001:db8:85a3:x")

    def test_ipv4_mapped(self):
        self.assertEqual(pixel.truncate_ip("::ffff:10.1.2.3"), "10.1.2.x")

    def test_garbage(self):
        self.assertIsNone(pixel.truncate_ip("not-an-ip"))
        self.assertIsNone(pixel.truncate_ip(None))

    def test_geo_key(self):
        self.assertEqual(pixel.geo_key("151.38.12.x"), "151.38.12.0")
        self.assertEqual(pixel.geo_key("2001:db8:85a3:x"), "2001:db8:85a3::")


class Clean(unittest.TestCase):
    def test_path(self):
        self.assertEqual(pixel.clean_path("/posts/chi-accende-la-luce/"), "/posts/chi-accende-la-luce/")
        self.assertEqual(pixel.clean_path("/a?x=1#y"), "/a")
        self.assertIsNone(pixel.clean_path("https://evil.example/"))
        self.assertIsNone(pixel.clean_path("/<script>"))
        self.assertIsNone(pixel.clean_path(""))

    def test_referrer(self):
        self.assertEqual(pixel.clean_referrer("www.google.com"), "google.com")
        self.assertEqual(pixel.clean_referrer("https://news.ycombinator.com/item?id=1"), "news.ycombinator.com")
        self.assertIsNone(pixel.clean_referrer("borgateo.com"))
        self.assertIsNone(pixel.clean_referrer("not a host"))

    def test_ua(self):
        self.assertEqual(pixel.classify_ua(CHROME_MAC), ("Chrome", "desktop", 0))
        self.assertEqual(pixel.classify_ua(SAFARI_IPHONE), ("Safari", "mobile", 0))
        self.assertEqual(pixel.classify_ua("Googlebot/2.1")[2], 1)
        self.assertEqual(pixel.classify_ua("")[2], 1)

    def test_client_ip_prefers_netlify_header(self):
        h = Headers({"x-nf-client-connection-ip": "1.2.3.4", "x-forwarded-for": "9.9.9.9, 5.5.5.5"})
        self.assertEqual(pixel.client_ip(h), "1.2.3.4")
        self.assertEqual(pixel.client_ip(Headers({"x-forwarded-for": "9.9.9.9, 5.5.5.5"})), "9.9.9.9")


class Limits(unittest.TestCase):
    def test_per_network_and_global_budget(self):
        now = [0.0]
        rl = pixel.RateLimiter(per_key=2, total=3, window=60, clock=lambda: now[0])
        self.assertEqual([rl.allow("a"), rl.allow("a"), rl.allow("a")], [True, True, False])
        self.assertTrue(rl.allow("b"))
        self.assertFalse(rl.allow("c"))  # global budget used up
        now[0] = 61
        self.assertTrue(rl.allow("a"))  # new window

    def test_flood_is_capped(self):
        with pixel.db() as conn:
            conn.execute("DELETE FROM hits")
        pixel.limiter = pixel.RateLimiter(per_key=5, total=100)
        h = Headers({"user-agent": CHROME_MAC, "x-nf-client-connection-ip": "203.0.113.9"})
        stored = sum(pixel.record({"p": "/"}, h, None) for _ in range(50))
        self.assertEqual(stored, 5)
        pixel.limiter = pixel.RateLimiter(10**6, 10**6)


class Record(unittest.TestCase):
    def setUp(self):
        pixel.limiter = pixel.RateLimiter(10**6, 10**6)
        with pixel.db() as conn:
            conn.execute("DELETE FROM hits")
            conn.execute("DELETE FROM daily_totals")

    def rows(self):
        with pixel.db() as conn:
            return conn.execute("SELECT path, referrer, browser, device, is_bot, is_return, is_owner, ip_trunc FROM hits").fetchall()

    def test_stores_truncated_ip_only(self):
        h = Headers({"user-agent": SAFARI_IPHONE, "x-nf-client-connection-ip": "151.38.12.47"})
        self.assertTrue(pixel.record({"p": "/posts/x/", "r": "www.google.com", "v": "1", "o": "0"}, h, None))
        self.assertEqual(self.rows(), [("/posts/x/", "google.com", "Safari", "mobile", 0, 1, 0, "151.38.12.x")])
        raw = Path(pixel.DB_PATH).read_bytes()
        self.assertNotIn(b"151.38.12.47", raw)

    def test_owner_flag(self):
        h = Headers({"user-agent": CHROME_MAC})
        pixel.record({"p": "/", "o": "1"}, h, None)
        self.assertEqual(self.rows()[0][6], 1)

    def test_respects_dnt_and_gpc(self):
        self.assertFalse(pixel.record({"p": "/"}, Headers({"dnt": "1"}), None))
        self.assertFalse(pixel.record({"p": "/"}, Headers({"sec-gpc": "1"}), None))
        self.assertEqual(self.rows(), [])

    def test_invalid_path_ignored(self):
        self.assertFalse(pixel.record({"p": "javascript:alert(1)"}, Headers({}), None))

    def test_retention_rolls_up_and_deletes(self):
        with pixel.db() as conn:
            old = (dt.date(2026, 11, 19) - dt.timedelta(days=400)).isoformat()
            for owner in (0, 0, 1):
                conn.execute("INSERT INTO hits (ts, day, path, is_owner) VALUES (?, ?, '/a', ?)", (old + "T00:00:00Z", old, owner))
            conn.execute("INSERT INTO hits (ts, day, path) VALUES ('2026-11-18T00:00:00Z', '2026-11-18', '/b')")
            removed = pixel.apply_retention(conn, today=dt.date(2026, 11, 19))
            self.assertEqual(removed, 3)
            self.assertEqual(conn.execute("SELECT day, path, views, owner_views FROM daily_totals").fetchall(), [(old, "/a", 2, 1)])
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM hits").fetchone()[0], 1)

    def test_stats_page_renders(self):
        pixel.record({"p": "/"}, Headers({"user-agent": CHROME_MAC}), None)
        page = pixel.stats_html(30)
        self.assertIn("borgateo.com · visite", page)
        self.assertIn("<td>/</td>", page)


if __name__ == "__main__":
    unittest.main()
