import typing

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema

from aioe621.schemas.tags import Tag

if typing.TYPE_CHECKING:
    from aioe621.endpoints.endpoint import TagsType, TagType
    from aioe621.enums import PostRating, PostSortOrder


class TagSet(set[str]):
    def __init__(self, tags: "TagsType | None" = None) -> None:
        if isinstance(tags, (str, Tag)):
            tags = (tags,)
        super().__init__(map(str, tags or set()))

    def __add__(self, other: "TagSet") -> "TagSet":
        return TagSet(self.union(other))

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(set[str]))

    def with_tags(self, other: typing.Iterable["TagType"]) -> "TagSet":
        self.update(TagSet(other))
        return self

    def with_tag(self, tag: "TagType") -> "TagSet":
        self.add(str(tag))
        return self

    def with_order(self, order: "PostSortOrder | str | None") -> "TagSet":
        if order is not None:
            return self.with_tag(f"order:{order}")
        return self

    def with_blacklist(self, blacklist: "typing.Iterable[TagsType]") -> "TagSet":
        return self.with_tags(f"-( {TagSet(rule).flatten()} )" for rule in blacklist)

    def with_rating(self, rating: "PostRating | str | None") -> "TagSet":
        if rating is not None:
            return self.with_tag(f"rating:{rating}")
        return self

    def negate(self) -> "TagSet":
        return TagSet(tag if tag.startswith("-") else "-" + tag for tag in self)

    def flatten(self, do_sort: bool = True) -> str:
        return " ".join(sorted(self) if do_sort else self)

    def __str__(self) -> str:
        return self.flatten()
