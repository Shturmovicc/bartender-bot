from datetime import datetime, timezone

from ..models import UserDrink, UserGlass, UserIngredient
from .base import Mixin


class UsersMixin(Mixin):
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
