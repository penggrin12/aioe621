import typing

if typing.TYPE_CHECKING:
    from ..client import Client


class Endpoint:
    def __init__(self, client: "Client") -> None:
        self._client = client

        self._request = client._request
        self._request_model = self._client._request_model
