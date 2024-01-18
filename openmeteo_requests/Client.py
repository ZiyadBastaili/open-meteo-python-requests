"""Open-Meteo API client based on the requests library
Changes made:
- Added proxy support for improved data retrieval.
- Added Amazon API Gateway.
"""
from __future__ import annotations
from typing import TypeVar
import requests
from openmeteo_sdk.WeatherApiResponse import WeatherApiResponse
from urllib.parse import urlparse

T = TypeVar("T")
TSession = TypeVar("TSession", bound=requests.Session)


class OpenMeteoRequestsError(Exception):
    """Open-Meteo Error"""


class Client:
    """Open-Meteo API Client"""

    def __init__(self, session: TSession | None = None):
        self.session = session or requests.Session()

    def _get(self, cls: type[T], url: str, params: any, proxies: any, gateway: any) -> list[T]:
        params["format"] = "flatbuffers"
        if gateway:
            src_parsed = urlparse(api_endpoint_historical)
            src_no_path = "%s://%s" % (src_parsed.scheme, src_parsed.netloc)
            self.session.mount(src_no_path, gateway)
            response = self.session.get(url, params=params)
        elif proxies:
            response = self.session.get(url, params=params, proxies=proxies, verify=False)
        else:
            response = self.session.get(url, params=params)
        if response.status_code in [400, 429]:
            response_body = response.json()
            raise OpenMeteoRequestsError(response_body)

        response.raise_for_status()

        data = response.content
        messages = []
        total = len(data)
        pos = int(0)
        while pos < total:
            length = int.from_bytes(data[pos : pos + 4], byteorder="little")
            message = cls.GetRootAs(data, pos + 4)
            messages.append(message)
            pos += length + 4
        return messages

    def weather_api(self, url: str, params: any, proxies: any = None, gateway: any = None) -> list[WeatherApiResponse]:
        """Get and decode as weather api"""
        return self._get(WeatherApiResponse, url, params, proxies, gateway)

    def __del__(self):
        """cleanup"""
        self.session.close()
