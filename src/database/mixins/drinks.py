from typing import Optional

from ..models import Drink
from .base import Mixin

# fmt: off
__all__ = (
    'DrinksMixin',
)
# fmt: on


class DrinksMixin(Mixin):
    async def insert_drink(
        self,
        id: int,
        name: str,
        name_alternate: Optional[str],
        tags: Optional[str],
        category: Optional[str],
        alcoholic: bool,
        glass: int,
        instructions: Optional[str],
        thumbnail: Optional[str],
    ) -> None:
        query = """
        INSERT INTO drinks (id, name, name_alternate, tags, category, alcoholic, glass, instructions, thumbnail)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?);
        """

        await self.connection.execute(
            query, (id, name, name_alternate, tags, category, alcoholic, glass, instructions, thumbnail)
        )

    async def get_drink_by_name(self, name: str) -> Drink | None:
        query = """
        SELECT id, name, name_alternate, tags, category, alcoholic, glass, instructions, thumbnail
        FROM drinks
        WHERE name=? COLLATE NOCASE;
        """

        return await self._fetchone(Drink, query, (name,))

    async def get_drink_by_id(self, id: int) -> Drink | None:
        query = """
        SELECT id, name, name_alternate, tags, category, alcoholic, glass, instructions, thumbnail
        FROM drinks
        WHERE id=?;
        """

        return await self._fetchone(Drink, query, (id,))

    async def get_drink(self, name_or_id: str | int) -> Drink | None:
        if isinstance(name_or_id, str):
            if name_or_id.isdigit():
                return await self.get_drink_by_id(int(name_or_id))
            return await self.get_drink_by_name(name_or_id.strip())
        else:
            return await self.get_drink_by_id(name_or_id)

    async def get_random_drink(self) -> Drink | None:
        query = """
        SELECT id, name, name_alternate, tags, category, alcoholic, glass, instructions, thumbnail
        FROM drinks
        ORDER BY RANDOM()
        LIMIT 1;
        """

        return await self._fetchone(Drink, query)
