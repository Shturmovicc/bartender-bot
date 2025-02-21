from ..models import Glass
from .base import Mixin

# fmt: off
__all__ = (
    'GlassesMixin',
)
# fmt: on


class GlassesMixin(Mixin):
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

    async def get_glass_by_name(self, name: str) -> list[Glass]:
        query = """
        SELECT id, name
        FROM glasses
        WHERE name LIKE ?;
        """

        return await self._fetchall(Glass, query, (f'%{name}%',))

    async def get_glass_by_id(self, id: int) -> Glass | None:
        query = """
        SELECT id, name
        FROM glasses
        WHERE id=?;
        """

        return await self._fetchone(Glass, query, (id,))

    async def get_glass(self, name_or_id: str | int) -> list[Glass] | Glass | None:
        if isinstance(name_or_id, str):
            if name_or_id.isdigit():
                item = await self.get_glass_by_id(int(name_or_id))
            else:
                item = await self.get_glass_by_name(name_or_id.strip())
        else:
            item = await self.get_glass_by_id(name_or_id)

        if not item:
            return None
        elif isinstance(item, list) and len(item) == 1:
            return item[0]

        return item

    async def get_random_glass(self) -> Glass | None:
        query = """
        SELECT id, name
        FROM glasses
        ORDER BY RANDOM()
        LIMIT 1;
        """

        return await self._fetchone(Glass, query)
