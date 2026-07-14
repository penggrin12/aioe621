from ..schemas import Post, _PostsListResponse, _PostsOnePostResponse
from .endpoint import Endpoint


class Posts(Endpoint):
    async def list(
        self,
        tags: list[str] | str,
        limit: int | None = None,
        page: int | None = None,
    ) -> list[Post]:
        if isinstance(tags, list):
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
