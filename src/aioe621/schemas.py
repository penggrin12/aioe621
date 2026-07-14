from datetime import datetime
from enum import Enum
from functools import cached_property
from typing import Literal, Mapping, NamedTuple

from pydantic import BaseModel, ConfigDict, Field


class APIModel(BaseModel):
    model_config = ConfigDict(frozen=True, ignored_types=(cached_property,))


class Auth(NamedTuple):
    username: str
    api_key: str


class BaseFile(APIModel):
    width: int
    height: int
    url: str | None = None  # Safest to make URL optional (deleted posts hide URLs)


class File(BaseFile):
    ext: str
    size: int
    md5: str


class PreviewFile(BaseFile):
    alt: str | None = None


class VideoAlternate(APIModel):
    fps: float
    codec: str
    size: int
    width: int
    height: int
    url: str | None = None


class Alternates(APIModel):
    has: bool = False
    original: VideoAlternate | None = None
    variants: Mapping[str, VideoAlternate] = Field(default_factory=dict)
    samples: Mapping[str, VideoAlternate] = Field(default_factory=dict)


class SampleFile(PreviewFile):
    has: bool
    alternates: Alternates


class PostScore(APIModel):
    up: int
    down: int
    total: int


class PostTags(APIModel):
    general: tuple[str, ...]
    artist: tuple[str, ...]
    contributor: tuple[str, ...]
    copyright: tuple[str, ...]
    character: tuple[str, ...]
    species: tuple[str, ...]
    invalid: tuple[str, ...]
    meta: tuple[str, ...]
    lore: tuple[str, ...]

    @cached_property
    def all(self) -> tuple[str, ...]:
        return (
            self.general
            + self.artist
            + self.contributor
            + self.copyright
            + self.character
            + self.species
            + self.invalid
            + self.meta
            + self.lore
        )


class PostFlags(APIModel):
    pending: bool
    flagged: bool
    note_locked: bool
    status_locked: bool
    rating_locked: bool
    deleted: bool


class Rating(str, Enum):
    SAFE = "s"
    QUESTIONABLE = "q"
    EXPLICIT = "e"


class Relationships(APIModel):
    parent_id: int | None = None
    has_children: bool
    has_active_children: bool
    children: tuple[int, ...]


class Post(APIModel):
    id: int
    created_at: datetime
    updated_at: datetime

    file: File
    preview: PreviewFile
    sample: SampleFile

    score: PostScore
    tags: PostTags
    locked_tags: tuple[str, ...]
    change_seq: int
    flags: PostFlags
    rating: Rating

    fav_count: int
    sources: tuple[str, ...]
    pools: tuple[int, ...]
    relationships: Relationships

    approver_id: int | None = None
    uploader_id: int
    uploader_name: str
    description: str
    comment_count: int
    is_favorited: bool

    vote: int
    has_notes: bool
    duration: float | None = None


class _PostsListResponse(APIModel):
    posts: tuple[Post, ...]


class _PostsOnePostResponse(APIModel):
    post: Post


class _ErrorResponse(APIModel):
    success: Literal[False]
    reason: str
