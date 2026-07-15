import typing

from aioe621.schemas.tags import Tag

if typing.TYPE_CHECKING:
    from typing import Iterable, TypeAlias

    from aioe621.client import Client

    TagType: TypeAlias = str | Tag
    TagsType: TypeAlias = Iterable[TagType] | TagType


class Endpoint:
    def __init__(self, client: "Client") -> None:
        self._client = client

        self._request = client._request
        self._request_model = self._client._request_model

    def _flatten_tags(self, tags: "TagsType") -> str:
        if isinstance(tags, (str, Tag)):
            return str(tags)
        return " ".join(self._flatten_tags(tag) for tag in tags)
