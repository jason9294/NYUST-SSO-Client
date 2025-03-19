from typing import Literal, Optional

import requests

Method = Literal["GET", "POST", "PUT", "DELETE"]


class Route:
    def __init__(self, method: Method, url: str) -> None:
        self.method = method
        self.url = url


class HttpClient:
    def __init__(
        self,
        base_url: str = "",
        session: Optional[requests.Session] = None,
    ) -> None:
        self.base_url = base_url
        if session is None:
            self.session = requests.Session()

    def request(self, route: Route) -> requests.Response:
        url = f"{self.base_url}{route.url}"

        response = self.session.request(
            method=route.method,
            url=url,
        )

        return response
