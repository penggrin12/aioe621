from typing import Iterable

from aioe621.endpoints.endpoint import Endpoint
from aioe621.schemas import Post, _PostsListResponse, _PostsOnePostResponse


class Posts(Endpoint):
    async def list(
        self,
        tags: Iterable[str] | str,
        limit: int | None = None,
        page: int | None = None,
    ) -> tuple[Post, ...]:
        if not isinstance(tags, str):
            tags = " ".join(tags)

        return (
            await self._request_model(
                _PostsListResponse,
                "GET",
                "/posts.json",
                tags=tags,
                limit=limit,
                page=page,
            )
        ).posts

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
        return (
            await self._request_model(
                _PostsOnePostResponse,
                "GET",
                f"/posts/{id}.json",
            )
        ).post

    async def random(
        self,
    ) -> Post:
        return (
            await self._request_model(
                _PostsOnePostResponse,
                "GET",
                "/posts/random.json",
            )
        ).post
