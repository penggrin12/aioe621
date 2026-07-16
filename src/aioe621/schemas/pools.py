import typing
from datetime import datetime
from typing import Sequence

from aioe621.enums import PoolCategory
from aioe621.schemas.base import APIModel

if typing.TYPE_CHECKING:
    from aioe621.schemas.posts import Post


class Pool(APIModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime
    creator_id: int
    creator_name: str
    description: str
    is_active: bool
    category: PoolCategory
    post_ids: Sequence[int]
    post_count: int

    async def fetch_posts(self) -> Sequence["Post"]:
        return await self._client.posts.list(tags=f"pool:{self.id}")
