import typing
from functools import cached_property

from pydantic import BaseModel, ConfigDict, PrivateAttr

if typing.TYPE_CHECKING:
    from aioe621 import Client


class APIModel(BaseModel):
    _client: "Client" = PrivateAttr()  # technically should be nullable

    model_config = ConfigDict(
        frozen=True,
        ignored_types=(cached_property,),
        strict=True,
        extra="forbid",
    )


class _ErrorResponse(APIModel):
    success: typing.Literal[False]
    reason: str
