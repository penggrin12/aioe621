from typing import Sequence

from pydantic import TypeAdapter

from aioe621.endpoints.endpoint import Endpoint
from aioe621.enums import ForumCategory, ForumPostSortOrder, ForumTopicSortOrder
from aioe621.schemas.forum import ForumPost, ForumTopic


class Forum(Endpoint):
    async def topics(
        self,
        *,
        id: int | None = None,
        title: str | None = None,
        category: ForumCategory | None = None,
        is_sticky: bool | None = None,
        is_locked: bool | None = None,
        is_hidden: bool | None = None,
        order: ForumTopicSortOrder | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> Sequence[ForumTopic]:
        self._assert_in_range("id", id, (1, None))

        self._assert_in_range("limit", limit, (0, 320))
        self._assert_in_range("page", page, (1, 750))

        return await self._request_model(
            TypeAdapter(Sequence[ForumTopic]),
            "GET",
            "/forum_topics.json",
            **{
                "search[id]": id,
                "search[title_matches]": title,
                "search[order]": order,
                "search[category_id]": category,
                "search[is_sticky]": is_sticky,
                "search[is_locked]": is_locked,
                "search[is_hidden]": is_hidden,
            },
            limit=limit,
            page=page,
        )

    async def topic(self, id: int) -> ForumTopic:
        self._assert_in_range("id", id, (1, None))

        return await self._request_model(ForumTopic, "GET", f"/forum_topics/{id}.json")

    async def posts(
        self,
        *,
        id: int | Sequence[int] | None = None,
        creator_id: int | None = None,
        creator_name: str | None = None,
        topic_id: int | None = None,
        topic_title: str | None = None,
        body: str | None = None,
        topic_category: ForumCategory | None = None,
        is_hidden: bool | None = None,
        order: ForumPostSortOrder | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> Sequence[ForumPost]:
        self._assert_in_range("id", id, (1, None))
        self._assert_in_range("creator_id", creator_id, (1, None))
        self._assert_in_range("topic_id", topic_id, (1, None))

        self._assert_in_range("limit", limit, (0, 320))
        self._assert_in_range("page", page, (1, 750))

        return await self._request_model(
            TypeAdapter(Sequence[ForumPost]),
            "GET",
            "/forum_posts.json",
            **{
                "search[id]": id,
                "search[creator_id]": creator_id,
                "search[creator_name]": creator_name,
                "search[topic_title_matches]": topic_title,
                "search[topic_id]": topic_id,
                "search[topic_category_id]": topic_category,
                "search[body_matches]": body,
                "search[order]": order,
                "search[is_hidden]": is_hidden,
            },
            limit=limit,
            page=page,
        )

    async def post(self, id: int) -> ForumPost:
        self._assert_in_range("id", id, (1, None))

        return await self._request_model(ForumPost, "GET", f"/forum_posts/{id}.json")
