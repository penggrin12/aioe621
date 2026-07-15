from typing import Sequence

from pydantic import TypeAdapter

from aioe621.endpoints.endpoint import Endpoint
from aioe621.enums import PoolCategory, PoolSortOrder
from aioe621.schemas.pools import Pool


class Pools(Endpoint):
    async def list(
        self,
        id: int | None = None,
        name: str | None = None,
        description: str | None = None,
        *,
        category: PoolCategory | None = None,
        creator_id: int | None = None,
        creator_name: str | None = None,
        order: PoolSortOrder | None = None,
        is_active: bool | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> Sequence[Pool]:
        if (id is None) and (name is None) and (description is None):
            raise ValueError("Either id or name or description is required.")
        if id and (id <= 0):
            raise ValueError("The pool ID must not be less than or equal to zero.")

        return await self._request_model(
            TypeAdapter(Sequence[Pool]),
            "GET",
            "/pools.json",
            **{
                "search[id]": id,
                "search[name_matches]": name,
                "search[description_matches]": description,
                "search[creator_id]": creator_id,
                "search[creator_name]": creator_name,
                "search[category]": category,
                "search[order]": order,
                "search[is_active]": is_active,
            },
            limit=limit,
            page=page,
        )

    search = list

    async def get(
        self,
        id: int,
    ) -> Pool:
        if id <= 0:
            raise ValueError("The pool ID must not be less than or equal to zero.")
        return await self._request_model(Pool, "GET", f"/pools/{id}.json")
