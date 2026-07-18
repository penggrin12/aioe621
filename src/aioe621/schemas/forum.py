from datetime import datetime
from typing import Sequence

from aioe621.enums import ForumCategory, WarningType
from aioe621.schemas.base import APIModel


class ForumTopic(APIModel):
    id: int
    creator_id: int
    updater_id: int  # bumped by
    title: str
    response_count: int
    is_sticky: bool
    is_locked: bool
    is_hidden: bool
    created_at: datetime
    updated_at: datetime
    category_id: ForumCategory
    creator_name: str
    updater_name: str

    async def fetch_posts(self) -> Sequence["ForumPost"]:
        return await self._client.forum.posts(topic_id=self.id)


class ForumPost(APIModel):
    id: int
    created_at: datetime
    updated_at: datetime
    body: str
    creator_id: int
    updater_id: int  # for mod edits I guess?
    topic_id: int
    is_hidden: bool
    warning_type: WarningType | None
    warning_user_id: int | None
    creator_name: str
    updater_name: str

    async def fetch_topic(self) -> "ForumTopic":
        return await self._client.forum.topic(id=self.topic_id)
