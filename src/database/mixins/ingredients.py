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

    async def get_ingredient_by_name(self, name: str) -> Ingredient | None:
        query = """
        SELECT id, name, description, type, alcohol
        FROM ingredients
        WHERE name=? COLLATE NOCASE;
        """

        return await self._fetchone(Ingredient, query, (name,))

    async def get_ingredient_by_id(self, id: int) -> Ingredient | None:
        query = """
        SELECT id, name, description, type, alcohol
        FROM ingredients
        WHERE id=?;
        """

        return await self._fetchone(Ingredient, query, (id,))

    async def get_ingredient(self, name_or_id: str | int) -> Ingredient | None:
        if isinstance(name_or_id, str):
            if name_or_id.isdigit():
                return await self.get_ingredient_by_id(int(name_or_id))
            return await self.get_ingredient_by_name(name_or_id.strip())
        else:
            return await self.get_ingredient_by_id(name_or_id)

    async def get_random_ingredient(self) -> Ingredient | None:
        query = """
        SELECT id, name, description, type, alcohol
        FROM ingredients
        ORDER BY RANDOM()
        LIMIT 1;
        """

        return await self._fetchone(Ingredient, query)
