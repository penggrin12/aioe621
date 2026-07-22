import typing
from collections.abc import Iterable, Set
from enum import Enum

import regex
from pydantic_core import CoreSchema, core_schema

from aioe621.schemas.tags import Tag as TagSchema

if typing.TYPE_CHECKING:
    from typing_extensions import Self

    from aioe621.endpoints.endpoint import TagsType, TagType
    from aioe621.enums import PostRating, PostSortOrder

REGEX_TOKENIZE = regex.compile(
    r'\G(?>\s*)(?<token>(?<prefix>[-~])?(?<body>(?<metatag>(?>\w+:(?>"[^"]+"(?=\s|\z)|'
    r'(?>"{0,2})(?!(?<=")(?=\s|\z))\S+)))|(?<group>(?>(?>\(\s+)(?<subquery>(?>(?!(?<=\s)\)'
    r"|(?>\s+)\))(?>[-~]?(?&metatag)|[-~]?(?&group)|(?>[^\s)]+|(?<!\s)\)+)*)(?>(?>\s+)(?!\)))?|"
    r"(?=(?<=\s)\)|(?>\s+)\)))+)(?>\s*)(?<=\s)\))(?=\s|\z))|(?<tag>\S+)))(?>\s*)"
)


class Tag:
    class Prefix(str, Enum):
        NONE = ""
        NEGATIVE = "-"
        OR = "~"

    _prefix: Prefix
    _raw: "str | TagSet"

    def __new__(cls, tag: "Self | TagsType") -> "Self":
        if type(tag) is cls:
            return tag
        return cls._construct(*cls._parse(tag))

    @classmethod
    def _construct(cls, prefix: Prefix, raw: "str | TagSet") -> "Self":
        self = super().__new__(cls)
        self._prefix, self._raw = prefix, raw
        return self

    @classmethod
    def _parse(cls, tag: "Self | TagsType") -> "tuple[Prefix, str | TagSet]":
        if isinstance(tag, cls):
            return tag._prefix, tag._raw

        match tag:
            case None | "":
                raise ValueError("A tag cannot be None or an empty string")
            case str() | TagSchema():
                raw: str = str(tag).strip()

                if (match := REGEX_TOKENIZE.fullmatch(raw)) and match.group("group"):
                    prefix_str = match.group("prefix") or ""
                    return Tag.Prefix(prefix_str), TagSet(match.group("subquery"))

                if (prefix := Tag._get_prefix(raw)) != Tag.Prefix.NONE:
                    raw = raw[1:]
                return prefix, raw
            case TagSet() | Set():
                return Tag.Prefix.NONE, TagSet(tag)
            case _:
                raise ValueError(f"A tag cannot be parsed from {type(tag)!r}")

    @staticmethod
    def _get_prefix(raw_tag: str) -> Prefix:
        if len(raw_tag) < 2:
            return Tag.Prefix.NONE
        for prefix in Tag.Prefix:
            if prefix.value and raw_tag[0] == prefix.value:
                return prefix
        return Tag.Prefix.NONE

    def __str__(self) -> str:
        return (
            self.prefix.value + self._raw
            if isinstance(self._raw, str)
            else f"{self.prefix.value}( {str(self._raw)} )"
        )

    def __repr__(self) -> str:
        return f"{type(self).__name__}(prefix={self.prefix!r}, raw={self._raw!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Tag):
            return self.prefix == other.prefix and self._raw == other._raw
        if isinstance(other, (str, TagSchema)):
            return str(self) == str(other)
        return NotImplemented

    def __hash__(self) -> int:
        return hash(str(self))

    @classmethod
    def __get_pydantic_core_schema__(cls, _, __) -> CoreSchema:
        return core_schema.no_info_plain_validator_function(cls)

    def as_negative(self) -> "Self":
        return type(self)._construct(Tag.Prefix.NEGATIVE, self._raw)

    def as_or(self) -> "Self":
        return type(self)._construct(Tag.Prefix.OR, self._raw)

    def as_no_prefix(self) -> "Self":
        return type(self)._construct(Tag.Prefix.NONE, self._raw)

    @property
    def prefix(self) -> Prefix:
        return self._prefix

    @property
    def is_plain(self) -> bool:
        return self.prefix == Tag.Prefix.NONE

    @property
    def is_negated(self) -> bool:
        return self.prefix == Tag.Prefix.NEGATIVE

    @property
    def is_or(self) -> bool:
        return self.prefix == Tag.Prefix.OR

    @property
    def is_group(self) -> bool:
        return isinstance(self._raw, TagSet)


class TagSet(frozenset[Tag]):
    def __new__(cls, tags: "TagsType | frozenset | set | None" = None) -> "Self":
        if type(tags) is cls:
            return tags

        match tags:
            case None | "":
                elements: Iterable[Tag] = ()
            case str() as t:
                elements = (Tag(x) for x in cls._iter_parse(t))
            case TagSchema() as t:
                elements = (Tag(x) for x in cls._iter_parse(str(t)))
            case Tag() as t:
                elements = (t,)
            case _:

                def _to_tag(t: "TagsType") -> Tag:
                    if isinstance(t, Tag):
                        return t
                    if isinstance(t, str):
                        return Tag(t)
                    if isinstance(t, Iterable):
                        return Tag(cls(t))
                    return Tag(str(t))

                elements = (_to_tag(t) for t in tags)

        return super().__new__(cls, typing.cast(Iterable[Tag], elements))

    def __add__(self, other: "TagSet") -> "Self":
        return self.with_tags(other)

    def __contains__(self, tag: object) -> bool:
        if isinstance(tag, str):
            tag = Tag(tag)
        return super().__contains__(tag)

    def __eq__(self, other: typing.Any) -> bool:
        if isinstance(other, Set):
            return super().__eq__(other)
        return NotImplemented

    __hash__ = frozenset.__hash__

    @classmethod
    def __get_pydantic_core_schema__(cls, _, __) -> CoreSchema:
        return core_schema.no_info_plain_validator_function(cls)

    @staticmethod
    def _iter_parse(tags: str) -> typing.Iterator[Tag | str]:
        for match in REGEX_TOKENIZE.finditer(tags):
            if match.group("group"):
                prefix_str = match.group("prefix") or ""
                yield Tag._construct(
                    Tag.Prefix(prefix_str), TagSet(match.group("subquery"))
                )
            else:
                yield match.group("token")

    def with_tags(self, other: "TagsType") -> "Self":
        return type(self)(super().union(type(self)(other)))

    def with_tag(self, tag: "TagType") -> "Self":
        return type(self)(super().union((Tag(tag),)))

    def with_order(
        self, order: "PostSortOrder | str | None", *, inverted: bool = False
    ) -> "Self":
        if order is None:
            return self
        order = order.value if isinstance(order, Enum) else order
        inverted = inverted or order.startswith("-")
        return self.with_tag(f"{'-' if inverted else ''}order:{order}")

    def with_blacklist(self, blacklist: "Iterable[TagsType]") -> "Self":
        return self.with_tags(
            f"-( {type(self)(rule).flattened()} )" for rule in blacklist
        )

    def with_rating(self, rating: "PostRating | str | None") -> "Self":
        if rating is None:
            return self
        return self.with_tag(f"rating:{rating}")

    def negated_tags(self) -> "Self":
        return super().__new__(type(self), (tag.as_negative() for tag in self))

    def as_strings(self) -> typing.Generator[str, None, None]:
        for tag in self:
            yield str(tag)

    def flattened(self, do_sort: bool = True) -> str:
        tags = self.as_strings()
        return " ".join(sorted(tags) if do_sort else tags)

    def __str__(self) -> str:
        return self.flattened()

    def __repr__(self) -> str:
        return f"{type(self).__name__}({str(self)!r})"
