import typing

import httpx
from pydantic import BaseModel

from aioe621 import endpoints
from aioe621.exceptions import (
    AccessDeniedError,
    APIError,
    AuthenticationError,
    NotFoundError,
)
from aioe621.schemas import _ErrorResponse

if typing.TYPE_CHECKING:
    from .schemas import Auth


class Client:
    E621_BASE_URL = "https://e621.net"
    E926_BASE_URL = "https://e926.net"

    def __init__(
        self,
        auth: "Auth | None" = None,
        base_url: str = E621_BASE_URL,
        user_agent: str | None = None,
        session: httpx.AsyncClient | None = None,
        **session_kwargs,
    ) -> None:
        self.auth: "Auth | None" = auth
        self.user_agent: str = (
            user_agent or "penggrin12/aioe621@github penggrin@telegram"
        )
        self.session: httpx.AsyncClient = session or httpx.AsyncClient(
            base_url=base_url,
            auth=httpx.BasicAuth(*self.auth) if self.auth else None,
            **session_kwargs,
        )

        self.posts = endpoints.Posts(self)

    def _get_headers(self) -> dict[str, str]:
        return {"User-Agent": self.user_agent}

    @staticmethod
    def _find_error(response: httpx.Response) -> APIError:
        error = _ErrorResponse.model_validate_json(response.text)
        match error.reason.strip().casefold():
            case "not found":
                return NotFoundError(response)
            case "access denied":
                return AccessDeniedError(response)
            case _:
                return APIError(error.reason.capitalize(), response)

    async def _request(
        self,
        method: str,
        url: str,
        *,
        authorized: bool = False,
        **params,
    ) -> str:
        if authorized and (not self.auth):
            raise AuthenticationError(method, url)

        response = await self.session.request(
            method=method,
            url=url,
            params={k: v for k, v in params.items() if v is not None},
            headers=self._get_headers(),
        )

        if not response.is_error:
            return response.text

        raise self._find_error(response)

    _MT = typing.TypeVar("_MT", bound="BaseModel")

    async def _request_model(
        self,
        model: type[_MT],
        method: str,
        url: str,
        **kwargs,
    ) -> _MT:
        return model.model_validate_json(
            await self._request(
                method=method,
                url=url,
                **kwargs,
            )
        )
