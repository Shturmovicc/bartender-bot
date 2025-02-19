import datetime
import sqlite3
from datetime import datetime, timezone
from types import TracebackType
from typing import Any, Iterable, Optional, Self, Sequence, TypeVar

import aiosqlite

from .init import INIT_QUERY
from .models import Drink, DrinkIngredient, Glass, Ingredient, UserDrink, UserGlass, UserIngredient

# fmt: off
__all__ = (
    'Database',
)
# fmt: on


ContainerT = TypeVar('ContainerT', bound=object)


class Database:
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

    async def insert_glass(self, name: str) -> Glass:
        query = """
        INSERT INTO glasses (name)
        VALUES (?)
        RETURNING id, name;
        """

        row = await self._fetchone(Glass, query, (name,))

        if not row:
            raise ValueError('Failed to get inserted item.')

        return row

    async def get_glass_by_name(self, name: str) -> Glass | None:
        query = """
        SELECT id, name
        FROM glasses
        WHERE name=? COLLATE NOCASE;
        """

        return await self._fetchone(Glass, query, (name,))

    async def get_glass_by_id(self, id: int) -> Glass | None:
        query = """
        SELECT id, name
        FROM glasses
        WHERE id=?;
        """

        return await self._fetchone(Glass, query, (id,))

    async def get_glass(self, name_or_id: str | int) -> Glass | None:
        if isinstance(name_or_id, str):
            if name_or_id.isdigit():
                return await self.get_glass_by_id(int(name_or_id))
            return await self.get_glass_by_name(name_or_id.strip())
        else:
            return await self.get_glass_by_id(name_or_id)

    async def get_random_glass(self) -> Glass | None:
        query = """
        SELECT id, name
        FROM glasses
        ORDER BY RANDOM()
        LIMIT 1;
        """

        return await self._fetchone(Glass, query)

    async def get_glass_drinks(self, id: int) -> list[Drink]:
        query = """
        SELECT id, name, name_alternate, tags, category, alcoholic, glass, instructions, thumbnail
        FROM drinks
        WHERE glass=?;
        """

        return await self._fetchall(Drink, query, (id,))

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

    async def create_user(self, id: int, name: str) -> None:
        query = """
        INSERT INTO users (id, name, created)
        VALUES (?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET name = excluded.name;
        """

        await self.connection.execute(query, (id, name, datetime.now(tz=timezone.utc)))

    async def get_user_drinks(self, id: int) -> list[UserDrink]:
        query = """
        SELECT id, name, name_alternate, tags, category, alcoholic, glass, instructions, thumbnail, amount
        FROM drink_inventory
        LEFT JOIN drinks ON drink_inventory.drink_id = drinks.id
        WHERE user_id=?
        ORDER BY amount DESC, name;
        """

        return await self._fetchall(UserDrink, query, (id,))

    async def get_user_glasses(self, id: int) -> list[UserGlass]:
        query = """
        SELECT id, name, amount
        FROM glass_inventory
        LEFT JOIN glasses ON glass_inventory.glass_id = glasses.id
        WHERE user_id=?
        ORDER BY amount DESC, name;
        """

        return await self._fetchall(UserGlass, query, (id,))

    async def get_user_ingredients(self, id: int) -> list[UserIngredient]:
        query = """
        SELECT id, name, description, type, alcohol, amount
        FROM ingredient_inventory
        LEFT JOIN ingredients ON ingredient_inventory.ingredient_id = ingredients.id
        WHERE user_id=?
        ORDER BY amount DESC, name;
        """

        return await self._fetchall(UserIngredient, query, (id,))

    async def _set_user_drink(self, user_id: int, drink_id: int, amount: float) -> None:
        query = """
        INSERT INTO drink_inventory (user_id, drink_id, amount, modified)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id, drink_id) DO UPDATE SET
            amount = excluded.amount, modified = excluded.modified;
        """

        await self.connection.execute(query, (user_id, drink_id, amount, datetime.now(tz=timezone.utc)))

    async def _delete_user_drink(self, user_id: int, drink_id: int) -> None:
        query = """
        DELETE FROM drink_inventory
        WHERE user_id = ? AND drink_id = ?;
        """

        await self.connection.execute(query, (user_id, drink_id))

    async def set_user_drink(self, user_id: int, drink_id: int, amount: float) -> None:
        if amount > 0:
            await self._set_user_drink(user_id, drink_id, amount)
        else:
            await self._delete_user_drink(user_id, drink_id)

    async def _set_user_glass(self, user_id: int, glass_id: int, amount: float) -> None:
        query = """
        INSERT INTO glass_inventory (user_id, glass_id, amount, modified)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id, glass_id) DO UPDATE SET
            amount = excluded.amount, modified = excluded.modified;
        """

        await self.connection.execute(query, (user_id, glass_id, amount, datetime.now(tz=timezone.utc)))

    async def _delete_user_glass(self, user_id: int, glass_id: int) -> None:
        query = """
        DELETE FROM glass_inventory
        WHERE user_id = ? AND glass_id = ?;
        """

        await self.connection.execute(query, (user_id, glass_id))

    async def set_user_glass(self, user_id: int, glass_id: int, amount: float) -> None:
        if amount > 0:
            await self._set_user_glass(user_id, glass_id, amount)
        else:
            await self._delete_user_glass(user_id, glass_id)

    async def _set_user_ingredient(self, user_id: int, ingredient_id: int, amount: float) -> None:
        query = """
        INSERT INTO ingredient_inventory (user_id, ingredient_id, amount, modified)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id, ingredient_id) DO UPDATE SET
            amount = excluded.amount, modified = excluded.modified;
        """

        await self.connection.execute(query, (user_id, ingredient_id, amount, datetime.now(tz=timezone.utc)))

    async def _delete_user_ingredient(self, user_id: int, ingredient_id: int) -> None:
        query = """
        DELETE FROM ingredient_inventory
        WHERE user_id = ? AND ingredient_id = ?;
        """

        await self.connection.execute(query, (user_id, ingredient_id))

    async def set_user_ingredient(self, user_id: int, ingredient_id: int, amount: float) -> None:
        if amount > 0:
            await self._set_user_ingredient(user_id, ingredient_id, amount)
        else:
            await self._delete_user_ingredient(user_id, ingredient_id)

    async def search_drinks(self, ingredients: Sequence[int], glass: Optional[int] = None) -> list[Drink]:
        query = f"""
        SELECT d.id, d.name, d.name_alternate, d.tags, d.category, d.alcoholic, d.glass, d.instructions, d.thumbnail
        FROM drinks AS d
        {f'JOIN drink_ingredients AS di ON di.drink_id = d.id AND di.ingredient_id in ({",".join("?" for _ in ingredients)})' if ingredients else ''}
        {'WHERE d.glass = ?' if glass else ''}
        GROUP BY d.id
        {'HAVING COUNT(DISTINCT di.ingredient_id) >= ?' if ingredients else ''}
        ORDER BY d.name;
        """

        params: list[int] = []
        if ingredients:
            params.extend(ingredients)
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
