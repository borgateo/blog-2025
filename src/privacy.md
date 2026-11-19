---
layout: default
title: Privacy
path: privacy
description: What this site collects about visits, and what it doesn't.
language: en
permalink: /privacy/
---

<div class="container max-w-3xl mx-auto mt-11 px-5 font-serif text-base"><article class="prose-xl lg:prose-2xl">

# Privacy

This blog has no cookies, no ads and no third-party trackers.

To know which posts people read, a few lines of JavaScript send one request per page view to my own server, a Raspberry Pi at home. It records:

- the page you opened and the time;
- the website you came from, only its domain (e.g. `google.com`);
- your browser and device type (e.g. Safari on mobile), mostly to filter out bots;
- your country and network provider, worked out from your IP address;
- your IP address **shortened**: the last part is replaced with an `x` (e.g. `151.38.12.x`), so it points to a network, not to you. The full address is never stored or logged.

Your browser keeps a small “visited before” flag in its local storage, so I can tell new visits from returning ones. It holds a date and nothing else: no ID, nothing that links your visits together on my side. It resets after 13 months, and you can clear it any time with your browser data.

If your browser sends **Do Not Track** or **Global Privacy Control**, nothing is sent at all.

Detailed records are kept for 13 months. After that only daily totals per page remain. Nothing is shared or sold.

Fonts and scripts are served from this site. The only other service that sees your request is [Netlify](https://www.netlify.com/privacy/), which hosts it.

The code is public: [github.com/borgateo/blog-2025](https://github.com/borgateo/blog-2025/tree/main/pixel). IP geolocation by [DB-IP](https://db-ip.com).

</article></div>
