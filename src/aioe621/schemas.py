from datetime import datetime
from enum import Enum
from typing import NamedTuple

from pydantic import BaseModel, Field


class Auth(NamedTuple):
    username: str
    api_key: str


class BaseFile(BaseModel):
    width: int
    height: int
    url: str | None = None  # Safest to make URL optional (deleted posts hide URLs)


class File(BaseFile):
    ext: str
    size: int
    md5: str


class PreviewFile(BaseFile):
    alt: str | None = None


class VideoAlternate(BaseModel):
    fps: int
    codec: str
    size: int
    width: int
    height: int
    url: str | None = None


class Alternates(BaseModel):
    has: bool = False
    original: VideoAlternate | None = None
    variants: dict[str, VideoAlternate] = Field(default_factory=dict)
    samples: dict[str, VideoAlternate] = Field(default_factory=dict)


class SampleFile(PreviewFile):
    has: bool
    alternates: Alternates


class PostScore(BaseModel):
    up: int
    down: int
    total: int


class PostTags(BaseModel):
    general: list[str]
    artist: list[str]
    contributor: list[str]
    copyright: list[str]
    character: list[str]
    species: list[str]
    invalid: list[str]
    meta: list[str]
    lore: list[str]


class PostFlags(BaseModel):
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


class Relationships(BaseModel):
    parent_id: int | None = None
    has_children: bool
    has_active_children: bool
    children: list[int]


class Post(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime

    file: File
    preview: PreviewFile
    sample: SampleFile

    score: PostScore
    tags: PostTags
    locked_tags: list[str]
    change_seq: int
    flags: PostFlags
    rating: Rating

    fav_count: int
    sources: list[str]
    pools: list[int]
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


class _PostsListResponse(BaseModel):
    posts: list[Post]


class _PostsOnePostResponse(BaseModel):
    post: Post
