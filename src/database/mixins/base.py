from typing import Any, Iterable, Optional, TypeVar

import aiosqlite

ContainerT = TypeVar('ContainerT', bound=object)


class Mixin:
    connection: aiosqlite.Connection

    async def _fetchone(
        self,
        container: type[ContainerT],
        query: str,
        params: Optional[Iterable[Any]] = None,
    ) -> ContainerT | None:
        async with self.connection.execute(query, params) as cursor:
            row = await cursor.fetchone()

        if row is not None:
            row = container(**row)

        return row

    async def _fetchall(
        self,
        container: type[ContainerT],
        query: str,
        params: Optional[Iterable[Any]] = None,
    ) -> list[ContainerT]:
        async with self.connection.execute(query, params) as cursor:
            row = await cursor.fetchall()

        return [container(**i) for i in row]
