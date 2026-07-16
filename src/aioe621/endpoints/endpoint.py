import typing

if typing.TYPE_CHECKING:
    from typing import Iterable, TypeAlias

    from aioe621.client import Client
    from aioe621.objects import TagSet
    from aioe621.schemas.tags import Tag

    TagType: TypeAlias = "str | Tag"
    TagsType: TypeAlias = "TagSet | Iterable[TagType] | TagType"


class Endpoint:
    def __init__(self, client: "Client") -> None:
        self._client = client

        self._request = client._request
        self._request_model = self._client._request_model
