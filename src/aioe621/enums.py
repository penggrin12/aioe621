from enum import Enum


class PostRating(str, Enum):
    SAFE = "s"
    QUESTIONABLE = "q"
    EXPLICIT = "e"


class PostSortOrder(str, Enum):
    ID = "id"
    SCORE = "score"
    FAVCOUNT = "favcount"
    COMMENT_COUNT = "comment_count"
    COMMENT_BUMPED = "comment_bumped"
    MPIXELS = "mpixels"
    FILESIZE = "filesize"
    LANDSCAPE = "landscape"
    CHANGE = "change"
    DURATION = "duration"
    RANDOM = "random"
    COMMENT = "comment"
    CREATED = "created"
    UPDATED = "updated"
    NOTE = "note"
    TAGCOUNT = "tagcount"
    GENERAL_TAGS = "general_tags"
    ARTIST_TAGS = "artist_tags"
    CONTRIBUTOR_TAGS = "contributor_tags"
    COPYRIGHT_TAGS = "copyright_tags"
    CHARACTER_TAGS = "character_tags"
    SPECIES_TAGS = "species_tags"
    INVALID_TAGS = "invalid_tags"
    META_TAGS = "meta_tags"
    LORE_TAGS = "lore_tags"
    MD5 = "md5"


class TagSortOrder(str, Enum):
    ID_ASCENDING = "id_asc"
    ID_DESCENDING = "id_desc"
    NAME = "name"
    DATE = "date"
    COUNT = "count"
    SIMILARITY = "similarity"


class TagCategory(int, Enum):
    GENERAL = 0
    ARTIST = 1
    CONTRIBUTOR = 2
    COPYRIGHT = 3
    CHARACTER = 4
    SPECIES = 5
    INVALID = 6
    META = 7
    LORE = 8


class PoolCategory(str, Enum):
    SERIES = "series"
    COLLECTION = "collection"


class PoolSortOrder(str, Enum):
    ID_ASCENDING = "id_asc"
    ID_DESCENDING = "id_desc"
    NAME = "name"
    CREATED_AT = "created_at"
    POST_COUNT = "post_count"
