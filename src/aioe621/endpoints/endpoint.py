import typing

if typing.TYPE_CHECKING:
    from typing import Iterable, TypeAlias

    from aioe621.client import Client
    from aioe621.objects import TagSet
    from aioe621.schemas.tags import Tag

    TagType: TypeAlias = "str | Tag"
    TagsType: TypeAlias = "TagSet | Iterable[TagType | TagSet] | TagType"


class Endpoint:
    def __init__(self, client: "Client") -> None:
        self._client = client

        self._request = client._request
        self._request_model = self._client._request_model

    @staticmethod
    def _assert_in_range(
        param_name: str,
        param_value: int | float | typing.Iterable[int | float] | None,
        range: tuple[int | float, int | float | None],
    ) -> None:
        """
        :raises ValueError: If `param_value` is out of `range`.
        """

        if param_value is None:
            return
        if not isinstance(param_value, (int, float)):
            for i, val in enumerate(param_value):
                Endpoint._assert_in_range(f"{param_name}[{i}]", val, range)
            return

        if param_value >= range[0]:
            if (range[1] is None) or (param_value <= range[1]):
                return

        raise ValueError(
            f"{param_name} must be in the range [{range[0]}..{range[1] or ''}] inclusive (given: {param_value})."
        )
