from typing import Optional

from ..models import Ingredient
from .base import Mixin

# fmt: off
__all__ = (
    'IngredientsMixin',
)
# fmt: on


class IngredientsMixin(Mixin):
    async def insert_ingredient(
        self,
        id: int,
        name: str,
        description: Optional[str],
        type: Optional[str],
        alcohol: bool,
    ) -> None:
        query = """
        INSERT INTO ingredients (id, name, description, type, alcohol)
        VALUES(?, ?, ?, ?, ?);
        """

        await self.connection.execute(query, (id, name, description, type, alcohol))

    async def get_ingredient_by_name(self, name: str) -> list[Ingredient]:
        query = """
        SELECT id, name, description, type, alcohol
        FROM ingredients
        WHERE name LIKE ?;
        """

        return await self._fetchall(Ingredient, query, (f'%{name}%',))

    async def get_ingredient_by_id(self, id: int) -> Ingredient | None:
        query = """
        SELECT id, name, description, type, alcohol
        FROM ingredients
        WHERE id=?;
        """

        return await self._fetchone(Ingredient, query, (id,))

    async def get_ingredient(self, name_or_id: str | int) -> list[Ingredient] | Ingredient | None:
        if isinstance(name_or_id, str):
            if name_or_id.isdigit():
                item = await self.get_ingredient_by_id(int(name_or_id))
            else:
                item = await self.get_ingredient_by_name(name_or_id.strip())
        else:
            item = await self.get_ingredient_by_id(name_or_id)

        if not item:
            return None
        elif isinstance(item, list) and len(item) == 1:
            return item[0]

        return item

    async def get_random_ingredient(self) -> Ingredient | None:
        query = """
        SELECT id, name, description, type, alcohol
        FROM ingredients
        ORDER BY RANDOM()
        LIMIT 1;
        """

        return await self._fetchone(Ingredient, query)
