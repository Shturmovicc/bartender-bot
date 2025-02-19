import logging
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

import config
from embeds import drink_embed, ingredient_embed
from exceptions import NotFoundError
from utils import cog_logging_wrapper

if TYPE_CHECKING:
    from main import CustomBot

logger = logging.getLogger(__name__)


class Random(commands.GroupCog, group_name='random'):
    def __init__(self, bot: 'CustomBot'):
        self.bot: 'CustomBot' = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{__name__} - loaded.')

    @app_commands.describe(full='Display full info about drink, defaults to False.')
    @app_commands.command(name='drink', description='Random drink from database.')
    @cog_logging_wrapper(logger=logger, skip_errors=(NotFoundError,))
    async def random_drink(self, interaction: discord.Interaction, full: bool = False) -> None:
        data = await self.bot.database.get_random_drink()
        if data:
            ingredients = await self.bot.database.get_drink_ingredients(data.id)
            glass = await self.bot.database.get_glass_by_id(data.glass)

            if not glass:
                raise IndexError(f'Failed to get glass from database.')

            embed = drink_embed(data, glass, ingredients, full=full)

            await interaction.followup.send(embed=embed)
        else:
            raise NotFoundError(f'No drinks been found.')

    @app_commands.describe(full='Display full info about ingredient, defaults to False.')
    @app_commands.command(name='ingredient', description='Random ingredient from database.')
    @cog_logging_wrapper(logger=logger, skip_errors=(NotFoundError,))
    async def random_ingredient(self, interaction: discord.Interaction, full: bool = False) -> None:
        data = await self.bot.database.get_random_ingredient()
        if data:
            embed = ingredient_embed(data, full=full)
            await interaction.followup.send(embed=embed)
        else:
            raise NotFoundError(f'No ingredients been found.')


async def setup(bot: 'CustomBot'):
    await bot.add_cog(
        Random(bot),
        guild=discord.Object(id=config.SERVER) if config.SERVER else None,
    )
