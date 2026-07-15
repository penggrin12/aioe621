from datetime import datetime
from enum import Enum
from functools import cached_property
from typing import Literal, TypeVar

from pydantic import Field

from aioe621.schemas.base import APIModel

_T = TypeVar("_T")


class FileDimensions(APIModel):
    width: int
    height: int


class File(FileDimensions):
    url: str | None


class PreviewFile(FileDimensions):
    jpg: str | None
    webp: str | None

    @property
    def url(self) -> str | None:
        return self.jpg or self.webp


class FilesMeta(APIModel):
    md5: str
    ext: str
    size: int
    duration: float | None
    has_sample: bool


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


class PostRating(str, Enum):
    SAFE = "s"
    QUESTIONABLE = "q"
    EXPLICIT = "e"


class VideoFile(File):
    fps: float
    codec: str  # TODO: "vp9" or "avc1.4D401E" or ...?
    size: int


class VideoVariants(APIModel):
    mp4: VideoFile | None = None
    # TODO: any more?


class VideoSamples(APIModel):
    p480: VideoFile | None = Field(alias="480p", default=None)
    p720: VideoFile | None = Field(alias="720p", default=None)


class Video(APIModel):
    has: Literal[True]
    original: VideoFile
    variants: VideoVariants
    samples: VideoSamples

    @property
    def url(self) -> str | None:
        return self.original.url


class PostFiles(APIModel):
    meta: FilesMeta
    original: File
    preview: PreviewFile
    sample: PreviewFile
    video: Video | None = None


class PostStats(APIModel):
    score: PostScore
    fav_count: int
    is_favorited: bool
    vote: int
    comment_count: int
    hotness: float


class PostHas(APIModel):
    parent: bool
    children: bool
    active_children: bool
    notes: bool
    sample: bool


class PostRelationships(APIModel):
    parent_id: int | None
    children: tuple[int, ...]


class Post(APIModel):
    id: int
    created_at: datetime
    updated_at: datetime
    change_seq: int
    files: PostFiles
    uploader_id: int
    uploader_name: str
    approver_id: int | None
    stats: PostStats
    flags: PostFlags
    has: PostHas
    relationships: PostRelationships
    pools: tuple[int, ...]
    rating: PostRating
    locked_tags: tuple[str, ...]
    sources: tuple[str, ...]
    description: str
    tags: PostTags

    async def fetch_children(self) -> tuple["Post", ...]:
        return await self._client.posts.list(f"parent:{self.id}")

    async def fetch_parent(self) -> "Post | None":
        if not self.relationships.parent_id:
            return None
        return await self._client.posts.get(id=self.relationships.parent_id)

    @property
    def score(self) -> PostScore:
        return self.stats.score

    @property
    def file(self) -> VideoFile | File:
        return self.files.video.original if self.files.video else self.files.original

    @property
    def url(self) -> str | None:
        return self.file.url
