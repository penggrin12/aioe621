from typing import Sequence

from pydantic import TypeAdapter

from aioe621.endpoints.endpoint import Endpoint
from aioe621.enums import TagSortOrder
from aioe621.schemas.tags import Tag, TagCategory


class Tags(Endpoint):
    async def list(
        self,
        query: str | None = None,
        *,
        order: TagSortOrder | None = None,
        category: TagCategory | None = None,
        hide_empty: bool | None = None,
        has_wiki: bool | None = None,
        has_artist: bool | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> Sequence[Tag]:
        return await self._request_model(
            TypeAdapter(Sequence[Tag]),
            "GET",
            "/tags.json",
            **{
                "search[name_matches]": query,
                "search[category]": category,
                "search[order]": order,
                "search[hide_empty]": hide_empty,
                "search[has_wiki]": has_wiki,
                "search[has_artist]": has_artist,
            },
            limit=limit,
            page=page,
        )

    search = list

    async def get(
        self,
        name: str,
    ) -> Tag | None:
        tags: Sequence[Tag] = await self.list(query=name, limit=1)
        return tags[0] if len(tags) > 0 else None
