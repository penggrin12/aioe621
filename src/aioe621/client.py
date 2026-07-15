import typing

import httpx
from pydantic import TypeAdapter

from aioe621 import endpoints
from aioe621.exceptions import (
    AccessDeniedError,
    APIError,
    AuthenticationError,
    NotFoundError,
)
from aioe621.schemas.base import APIModel, _ErrorResponse


class Auth(typing.NamedTuple):
    username: str
    api_key: str


class Client:
    E621_BASE_URL = "https://e621.net"
    E926_BASE_URL = "https://e926.net"

    def __init__(
        self,
        *,
        user_agent: str,
        auth: "Auth | None" = None,
        base_url: str = E621_BASE_URL,
        session: httpx.AsyncClient | None = None,
        **session_kwargs,
    ) -> None:
        self.auth: "Auth | None" = auth
        self.user_agent: str = (
            user_agent.strip() or "penggrin12/aioe621@github penggrin@telegram"
        )
        self.session: httpx.AsyncClient = session or httpx.AsyncClient(
            base_url=base_url,
            auth=httpx.BasicAuth(*self.auth) if self.auth else None,
            **session_kwargs,
        )

        self.posts = endpoints.Posts(self)
        self.tags = endpoints.Tags(self)

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

    _MT = typing.TypeVar("_MT", bound="APIModel")
    _T = typing.TypeVar("_T")

    def _inject_client(self, obj: _T) -> _T:
        if isinstance(obj, APIModel):
            obj.__dict__["_client"] = self
            typ: type[APIModel] = type(obj)

            for field_name in typ.model_fields.keys():
                field = getattr(obj, field_name)
                if isinstance(field, APIModel):
                    self._inject_client(field)
        elif isinstance(obj, typing.Mapping):
            for value in obj.values():
                self._inject_client(value)
        elif isinstance(obj, typing.Sequence) and not isinstance(
            obj, (str, bytes, bytearray)
        ):
            for item in obj:
                self._inject_client(item)
        return obj

    @typing.overload
    async def _request_model(
        self, model: TypeAdapter[_T], method: str, url: str, **kwargs
    ) -> _T: ...

    @typing.overload
    async def _request_model(
        self, model: type[_MT], method: str, url: str, **kwargs
    ) -> _MT: ...

    async def _request_model(
        self, model: type[_MT] | TypeAdapter[_T], method: str, url: str, **kwargs
    ) -> _MT | _T:
        json: str = await self._request(method=method, url=url, **kwargs)
        return self._inject_client(
            model.validate_json(json)
            if isinstance(model, TypeAdapter)
            else model.model_validate_json(json)
        )
