from __future__ import annotations

import time
from urllib.error import URLError
from urllib.request import Request, urlopen

from short_term_radar.data_sources.base import FetchResult


class HttpFetcher:
    def __init__(self, config: dict):
        fetch_cfg = config.get("fetch") or {}
        self.user_agent = fetch_cfg.get("user_agent", "short-term-radar-mvp/0.2")
        self.timeout = int(fetch_cfg.get("timeout_seconds", 30))
        self.retry_count = int(fetch_cfg.get("retry_count", 3))
        self.sleep_seconds = float(fetch_cfg.get("sleep_seconds", 1.0))

    def fetch_text(self, url: str, source: str, dataset: str) -> FetchResult:
        last_error: Exception | None = None
        for attempt in range(max(1, self.retry_count)):
            try:
                request = Request(url, headers={"User-Agent": self.user_agent})
                with urlopen(request, timeout=self.timeout) as response:
                    encoding = response.headers.get_content_charset() or "utf-8"
                    return FetchResult(source, dataset, url, raw_text=response.read().decode(encoding, errors="replace"))
            except URLError as exc:
                last_error = exc
                if attempt + 1 < self.retry_count:
                    time.sleep(self.sleep_seconds)
        return FetchResult(source, dataset, url, degraded=True, message=str(last_error))
