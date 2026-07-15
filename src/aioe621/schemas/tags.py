from datetime import datetime

from pydantic import field_validator

from aioe621.enums import TagCategory
from aioe621.schemas.base import APIModel


class RelatedTag(APIModel):
    name: str
    relatedness: int  # max 300


class Tag(APIModel):
    id: int
    name: str
    post_count: int
    related_tags: tuple[RelatedTag, ...]
    related_tags_updated_at: datetime
    category: TagCategory
    is_locked: bool
    created_at: datetime
    updated_at: datetime

    @field_validator("related_tags", mode="before")
    @classmethod
    def split_tags(cls, value: str):
        words = value.split(" ")
        related = []
        while len(words) >= 2:
            related.append(RelatedTag(name=words.pop(0), relatedness=int(words.pop(0))))
        return tuple(related)

    def __str__(self) -> str:
        return self.name
