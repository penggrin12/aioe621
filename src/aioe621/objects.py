import typing

import regex
from pydantic_core import CoreSchema, core_schema
from typing_extensions import Self

from aioe621.schemas.tags import Tag

if typing.TYPE_CHECKING:
    from aioe621.endpoints.endpoint import TagsType, TagType
    from aioe621.enums import PostRating, PostSortOrder

REGEX_TOKENIZE = regex.compile(
    r'\G(?>\s*)(?<token>(?<prefix>[-~])?(?<body>(?<metatag>(?>\w+:(?>"[^"]+"(?=\s|\z)|'
    r'(?>"{0,2})(?!(?<=")(?=\s|\z))\S+)))|(?<group>(?>(?>\(\s+)(?<subquery>(?>(?!(?<=\s)\)'
    r"|(?>\s+)\))(?>[-~]?(?&metatag)|[-~]?(?&group)|(?>[^\s)]+|(?<!\s)\)+)*)(?>(?>\s+)(?!\)))?|"
    r"(?=(?<=\s)\)|(?>\s+)\)))+)(?>\s*)(?<=\s)\))(?=\s|\z))|(?<tag>\S+)))(?>\s*)"
)


class TagSet(frozenset["str | TagSet"]):
    def __new__(cls, tags: "TagsType | frozenset | set | None" = None) -> Self:
        if type(tags) is cls:
            return tags

        match tags:
            case None | "":
                elements: typing.Iterable["str | TagSet"] = ()
            case str(t):
                elements = cls._iter_parse(t)
            case Tag() as t:
                elements = cls._iter_parse(str(t))
            case _:
                elements = (
                    t
                    if isinstance(t, (str, cls))
                    else cls(t)
                    if isinstance(t, typing.Iterable)
                    else str(t)
                    for t in tags
                )

        return super().__new__(
            cls, typing.cast(typing.Iterable["str | TagSet"], elements)
        )

    def __add__(self, other: "TagSet") -> Self:
        return self.with_tags(other)

    @classmethod
    def __get_pydantic_core_schema__(cls, _, __) -> CoreSchema:
        return core_schema.no_info_plain_validator_function(cls)

    @staticmethod
    def _iter_parse(tags: str) -> typing.Iterator["str | TagSet"]:
        for match in REGEX_TOKENIZE.finditer(tags):
            if match.group("group"):
                yield TagSet(match.group("subquery"))
            else:
                yield match.group("token")

    def with_tags(self, other: "TagsType") -> Self:
        return type(self)(super().union(type(self)(other)))

    def with_tag(self, tag: "TagType") -> Self:
        return type(self)(super().union((str(tag),)))

    def with_order(self, order: "PostSortOrder | str | None") -> Self:
        if order is None:
            return self
        return self.with_tag(f"order:{order}")

    def with_blacklist(self, blacklist: "typing.Iterable[TagsType]") -> Self:
        return self.with_tags(
            f"-( {type(self)(rule).flattened()} )" for rule in blacklist
        )

    def with_rating(self, rating: "PostRating | str | None") -> Self:
        if rating is None:
            return self
        return self.with_tag(f"rating:{rating}")

    def negated(self) -> Self:
        new_tags = frozenset(
            (tag if tag.startswith("-") else "-" + tag)
            if isinstance(tag, str)
            else (tag.negated())
            for tag in self
        )
        return type(self)(new_tags)

    def flattened(self, do_sort: bool = True) -> str:
        tags: typing.Generator[str, None, None] = (
            f"( {x.flattened()} )" if isinstance(x, TagSet) else x for x in self
        )
        return " ".join(sorted(tags) if do_sort else tags)

    def __str__(self) -> str:
        return self.flattened()
