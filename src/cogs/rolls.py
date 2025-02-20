import logging
import random
from typing import TYPE_CHECKING

import discord
from discord import Embed, app_commands
from discord.ext import commands

import config
from database.models import Drink, Glass, Ingredient
from embeds import drink_embed, glass_embed, ingredient_embed
from typedefs import ItemType
from utils import cog_logging_wrapper

if TYPE_CHECKING:
    from main import CustomBot

logger = logging.getLogger(__name__)

Data = Drink | Glass | Ingredient


def get_random_type() -> ItemType:
    percent = random.randint(0, 100)

    if percent > 10:
        return ItemType.INGREDIENT
    elif percent > 0:
        return ItemType.GLASS
    else:
        return ItemType.DRINK


class Rolls(commands.Cog):
    def __init__(self, bot: 'CustomBot'):
        self.bot: 'CustomBot' = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{__name__} - loaded.')

    async def get_random_data(self, type: ItemType) -> Data:
        if type == ItemType.INGREDIENT:
            data = await self.bot.database.get_random_ingredient()
        elif type == ItemType.GLASS:
            data = await self.bot.database.get_random_glass()
        elif type == ItemType.DRINK:
            data = await self.bot.database.get_random_drink()

        assert data
        return data

    async def get_current_data(self, type: ItemType, user: int):
        if type == ItemType.INGREDIENT:
            data = await self.bot.database.get_user_ingredients(user)
        elif type == ItemType.GLASS:
            data = await self.bot.database.get_user_glasses(user)
        elif type == ItemType.DRINK:
            data = await self.bot.database.get_user_drinks(user)

        return data

    async def set_data(self, type: ItemType, user_id: int, id: int, amount: float) -> None:
        if type == ItemType.INGREDIENT:
            await self.bot.database.set_user_ingredient(user_id, id, amount)
        elif type == ItemType.GLASS:
            await self.bot.database.set_user_glass(user_id, id, amount)
        elif type == ItemType.DRINK:
            await self.bot.database.set_user_drink(user_id, id, amount)

    async def get_data_embed(self, data: Data) -> Embed:
        if isinstance(data, Ingredient):
            embed = ingredient_embed(data, style='image')
        elif isinstance(data, Glass):
            embed = glass_embed(data)
        elif isinstance(data, Drink):

            glass = await self.bot.database.get_glass_by_id(data.glass)
            ingredients = await self.bot.database.get_drink_ingredients(data.id)

            assert glass
            assert ingredients

            embed = drink_embed(data, glass, ingredients)

        return embed

    @app_commands.command(name='roll', description='Roll for random ingredient, glass or drink.')
    @cog_logging_wrapper(logger=logger)
    async def roll(self, interaction: discord.Interaction) -> None:
        type = get_random_type()

        data = await self.get_random_data(type)

        async with self.bot.database:
            await self.bot.database.create_user(interaction.user.id, interaction.user.name)

            current = await self.get_current_data(type, interaction.user.id)

            exists = next(filter(lambda i: i.id == data.id, current), None)

            if exists:
                amount = exists.amount + 1
            else:
                amount = 1.0

            await self.set_data(type, user_id=interaction.user.id, id=data.id, amount=amount)

        if isinstance(amount, float) and amount.is_integer():
            amount = int(amount)

        embed = await self.get_data_embed(data)
        await interaction.followup.send(f'`You received {type}!`\n`Now you have {amount} in inventory.`', embed=embed)


async def setup(bot: 'CustomBot'):
    await bot.add_cog(
        Rolls(bot),
        guild=discord.Object(id=config.SERVER) if config.SERVER else None,
    )
