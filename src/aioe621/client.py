import base64
import typing

import httpx
from pydantic import BaseModel

from .endpoints.posts import Posts

if typing.TYPE_CHECKING:
    from .schemas import Auth


class Client:
    E621_BASE_URL = "https://e621.net"
    E926_BASE_URL = "https://e926.net"

    def __init__(
        self,
        auth: "Auth",
        base_url: str = E621_BASE_URL,
        user_agent: str | None = None,
        session: httpx.AsyncClient | None = None,
        **session_kwargs,
    ) -> None:
        self.auth = auth
        self.user_agent = user_agent or "penggrin12/aioe621@github penggrin@telegram"
        self.session = session or httpx.AsyncClient(base_url=base_url, **session_kwargs)

        self.posts = Posts(self)

    def _get_auth_header_value(self) -> str:
        return base64.b64encode(
            f"{self.auth.username}:{self.auth.api_key}".encode()
        ).decode()

    async def _request(
        self, method: str, url: str, *, authorized: bool = False, **params
    ) -> str:
        response = await self.session.request(
            method,
            url,
            params={k: v for k, v in params.items() if v is not None},
            headers={
                "User-Agent": self.user_agent,
                **(
                    {"Authorization": self._get_auth_header_value()}
                    if authorized
                    else {}
                ),
            },
        )
        return response.text

    _MT = typing.TypeVar("_MT", bound="BaseModel")

    async def _request_model(
        self, model: type[_MT], method: str, url: str, **kwargs
    ) -> _MT:
        return model.model_validate_json(
            await self._request(method=method, url=url, **kwargs)
        )
