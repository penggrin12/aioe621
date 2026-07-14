import httpx


class WrapperError(Exception):
    def __init__(self, message: str, method: str, url: str) -> None:
        self.method = method
        self.url = url
        super().__init__(f"{message} (caused by: {self.method} {self.url})")


class AuthenticationError(WrapperError):
    def __init__(self, method: str, url: str) -> None:
        super().__init__(
            "Requested endpoint requires an authenticated client.", method, url
        )


class APIError(Exception):
    def __init__(self, message: str, response: httpx.Response) -> None:
        self.method = response.request.method
        self.url = response.request.url
        super().__init__(
            f"{message} ({response.status_code} caused by: {self.method} {self.url})"
        )


class NotFoundError(APIError):
    def __init__(self, response: httpx.Response) -> None:
        super().__init__("Not found.", response)


class AccessDeniedError(APIError):
    def __init__(self, response: httpx.Response) -> None:
        super().__init__("Access denied.", response)
