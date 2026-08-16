"""Small HTTP wrapper that keeps external calls easy to replace in tests."""

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class UrlLibTransport:
    def get_json(self, url: str):
        request = Request(url, headers={"Accept": "application/json"})
        try:
            with urlopen(request, timeout=10) as response:
                return json.load(response)
        except HTTPError as error:
            raise RuntimeError(f"Request failed with HTTP {error.code}") from error
        except URLError as error:
            raise RuntimeError(f"Network request failed: {error.reason}") from error
