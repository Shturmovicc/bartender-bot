import datetime
import sqlite3
from datetime import datetime
from types import TracebackType
from typing import Optional, Self, Sequence

import aiosqlite

from .init import INIT_QUERY
from .mixins import DrinksMixin, GlassesMixin, IngredientsMixin, UsersMixin
from .models import Drink, DrinkIngredient

# fmt: off
__all__ = (
    'Database',
)
# fmt: on


class Database(DrinksMixin, GlassesMixin, IngredientsMixin, UsersMixin):
    def __init__(self, connection: aiosqlite.Connection):
        self.connection = connection
        self.connection.row_factory = sqlite3.Row

    async def __aenter__(self) -> Self:
        """Enters transaction that will commit on exit or rollback on error."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if exc_type is None:
            await self.connection.commit()
        else:
            await self.connection.rollback()

    async def init(self) -> None:
        await self.connection.executescript(INIT_QUERY)
        await self.connection.commit()

    async def insert_drink_ingredient(self, drink_id: int, ingredient_id: int, measure: Optional[str]) -> None:
        query = """
        INSERT INTO drink_ingredients (drink_id, ingredient_id, measure)
        VALUES (?, ?, ?);
        """

        await self.connection.execute(query, (drink_id, ingredient_id, measure))

    async def remove_drink_ingredient(self, drink_id: int, ingredient_id: int) -> None:
        query = """
        DELETE FROM drink_ingredients WHERE drink_id=? AND ingredient_id=?;
        """

        await self.connection.execute(query, (drink_id, ingredient_id))

    async def get_drink_ingredients(self, id: int) -> list[DrinkIngredient]:
        query = """
        SELECT id, name, description, type, alcohol, measure
        FROM drink_ingredients
        INNER JOIN ingredients ON drink_ingredients.ingredient_id = ingredients.id
        WHERE drink_id=?;
        """

        return await self._fetchall(DrinkIngredient, query, (id,))

    async def search_drinks(
        self,
        name: Optional[str] = None,
        ingredients: Sequence[int] = (),
        glass: Optional[int] = None,
    ) -> list[Drink]:
        query = f"""
        SELECT d.id, d.name, d.name_alternate, d.tags, d.category, d.alcoholic, d.glass, d.instructions, d.thumbnail
        FROM drinks AS d
        {f'JOIN drink_ingredients AS di ON di.drink_id = d.id AND di.ingredient_id in ({",".join("?" for _ in ingredients)})' if ingredients else ''}
        {'WHERE' if name or glass else ''}
        {'d.name LIKE ?' if name else ''}
        {'AND' if name and glass else ''}
        {'d.glass=?' if glass else ''}
        GROUP BY d.id
        {'HAVING COUNT(DISTINCT di.ingredient_id) >= ?' if ingredients else ''}
        ORDER BY d.name;
        """

        params: list[str | int] = []
        if ingredients:
            params.extend(ingredients)
        if name:
            params.append(f'%{name}%')
        if glass:
            params.append(glass)
        if ingredients:
            params.append(len(ingredients))

        return await self._fetchall(Drink, query, params)

    async def get_available_crafts(self, user_id: int) -> list[Drink]:
        query = """
        WITH required_ingredients AS (
            SELECT drink_id, COUNT(ingredient_id) AS required_count
            FROM drink_ingredients
            GROUP BY drink_id
        ),
        matching_ingredients AS (
            SELECT di.drink_id, ii.user_id, COUNT(DISTINCT di.ingredient_id) AS matched_count
            FROM drink_ingredients AS di
            JOIN ingredient_inventory AS ii ON di.ingredient_id = ii.ingredient_id
            WHERE user_id = ?
            GROUP BY di.drink_id, ii.user_id
        )
        SELECT d.id, d.name, d.name_alternate, d.tags, d.category, d.alcoholic, d.glass, d.instructions, d.thumbnail
        FROM drinks AS d
        JOIN glass_inventory ON d.glass = glass_inventory.glass_id
        JOIN required_ingredients AS ri ON d.id = ri.drink_id
        JOIN matching_ingredients AS mi ON d.id = mi.drink_id
        WHERE mi.matched_count = ri.required_count
        ORDER BY d.name;
        """

        return await self._fetchall(Drink, query, (user_id,))


def adapt_datetime(date: datetime) -> str:
    return date.isoformat()


def convert_datetime(val: bytes) -> datetime:
    return datetime.fromisoformat(val.decode())


def adapt_boolean(boolean: bool) -> int:
    return int(boolean)


def convert_boolean(val: bytes) -> bool:
    return bool(int(val.decode()))


aiosqlite.register_adapter(datetime, adapt_datetime)
aiosqlite.register_converter('datetime', convert_datetime)
aiosqlite.register_adapter(bool, adapt_boolean)
aiosqlite.register_converter('boolean', convert_boolean)
