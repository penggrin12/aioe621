from datetime import datetime
from enum import Enum
from functools import cached_property
from typing import Literal, NamedTuple

from pydantic import BaseModel, ConfigDict, Field


class APIModel(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        ignored_types=(cached_property,),
        strict=True,
        extra="forbid",
    )


class Auth(NamedTuple):
    username: str
    api_key: str


class FileDimensions(APIModel):
    width: int
    height: int


class BaseFile(FileDimensions):
    url: str | None


class PreviewFile(FileDimensions):
    jpg: str | None
    webp: str | None


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


class VideoFile(BaseFile):
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


class PostFiles(APIModel):
    meta: FilesMeta
    original: BaseFile
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


class _ErrorResponse(APIModel):
    success: Literal[False]
    reason: str
