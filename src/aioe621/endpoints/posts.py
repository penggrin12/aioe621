from typing import TYPE_CHECKING, Sequence

from pydantic import TypeAdapter

from aioe621.endpoints.endpoint import Endpoint
from aioe621.enums import PostSortOrder
from aioe621.objects import TagSet
from aioe621.schemas.posts import Post

if TYPE_CHECKING:
    from aioe621.endpoints.endpoint import TagsType


class Posts(Endpoint):
    async def list(
        self,
        tags: "TagsType",
        *,
        order: PostSortOrder | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> Sequence[Post]:
        return await self._request_model(
            TypeAdapter(Sequence[Post]),
            "GET",
            "/posts.json",
            tags=(
                TagSet(tags)
                .with_order(order)
                .with_blacklist(self._client.blacklist)
                .flatten()
            ),
            limit=limit,
            page=page,
            v2=True,
            mode="extended",
        )

    search = list

    async def get(
        self,
        id: int,
    ) -> Post:
        """
        :raises ValueError: If the post id is invalid. (less or equal to zero)
        :raises NotFound: If the post with the requested id doesn't exist.
        """
        if id <= 0:
            raise ValueError("The post ID must not be less than or equal to zero.")
        return await self._request_model(
            Post,
            "GET",
            f"/posts/{id}.json",
            v2=True,
            mode="extended",
        )

    async def random(
        self,
    ) -> Post:
        return await self._request_model(
            Post,
            "GET",
            "/posts/random.json",
            v2=True,
            mode="extended",
        )
