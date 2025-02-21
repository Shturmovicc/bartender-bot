from datetime import datetime, timezone

from typedefs import ItemType

from ..models import UserDrink, UserGlass, UserIngredient, UserSetItemSignature
from .base import Mixin

# fmt: off
__all__ = (
    'UsersMixin',
)
# fmt: on


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
        WHERE user_id=? AND amount > 0
        ORDER BY amount DESC, name;
        """

        return await self._fetchall(UserDrink, query, (id,))

    async def get_user_glasses(self, id: int) -> list[UserGlass]:
        query = """
        SELECT id, name, amount
        FROM glass_inventory
        LEFT JOIN glasses ON glass_inventory.glass_id = glasses.id
        WHERE user_id=? AND amount > 0
        ORDER BY amount DESC, name;
        """

        return await self._fetchall(UserGlass, query, (id,))

    async def get_user_ingredients(self, id: int) -> list[UserIngredient]:
        query = """
        SELECT id, name, description, type, alcohol, amount
        FROM ingredient_inventory
        LEFT JOIN ingredients ON ingredient_inventory.ingredient_id = ingredients.id
        WHERE user_id=? AND amount > 0
        ORDER BY amount DESC, name;
        """

        return await self._fetchall(UserIngredient, query, (id,))

    async def get_user_items(self, type: ItemType, id: int) -> list[UserDrink] | list[UserGlass] | list[UserIngredient]:
        if type == ItemType.INGREDIENT:
            data = await self.get_user_ingredients(id)
        elif type == ItemType.GLASS:
            data = await self.get_user_glasses(id)
        elif type == ItemType.DRINK:
            data = await self.get_user_drinks(id)

        return data

    async def set_user_items(self, type: ItemType, *values: UserSetItemSignature) -> None:
        if not values:
            raise ValueError('Not values been provided.')

        query = f"""
        INSERT INTO {type}_inventory (user_id, {type}_id, amount, modified)
        VALUES {','.join(['(?, ?, ?, ?)' for _ in values])}
        ON CONFLICT(user_id, {type}_id) DO UPDATE SET
            amount = excluded.amount, modified = excluded.modified;
        """

        utcnow = datetime.now(tz=timezone.utc)
        params: list[int | float | datetime] = []
        for value in values:
            params.extend((value.user_id, value.item_id, value.amount, utcnow))

        await self.connection.execute(query, params)

    async def set_user_drinks(self, *values: UserSetItemSignature) -> None:
        return await self.set_user_items(ItemType.DRINK, *values)

    async def set_user_glasses(self, *values: UserSetItemSignature) -> None:
        return await self.set_user_items(ItemType.GLASS, *values)

    async def set_user_ingredients(self, *values: UserSetItemSignature) -> None:
        return await self.set_user_items(ItemType.INGREDIENT, *values)
