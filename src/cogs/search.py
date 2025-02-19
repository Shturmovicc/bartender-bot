import logging
from typing import TYPE_CHECKING, Optional

import discord
from discord import app_commands
from discord.ext import commands

import config
from embeds import PaginationView, drink_embed, ingredient_embed, search_result_embed
from exceptions import ArgumentError, NotFoundError
from utils import cog_logging_wrapper

if TYPE_CHECKING:
    from main import CustomBot

logger = logging.getLogger(__name__)


class Search(commands.GroupCog, group_name='search'):
    def __init__(self, bot: 'CustomBot'):
        self.bot: 'CustomBot' = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{__name__} - loaded.')

    @app_commands.rename(ingredient_name='ingredient', glass_name='glass')
    @app_commands.describe(
        name='Name or ID of drink, takes priority over `ingredient` and `glass`.',
        ingredient_name='Name or ID of ingredients separated by comma that will be used in search, cannot be used with `name`.',
        glass_name='Name or ID of glass that will be used in search, cannot be used with `name`.',
        full='Display full info about drink, defaults to False.',
    )
    @app_commands.command(name='drink', description='Search for drink.')
    @cog_logging_wrapper(logger=logger, skip_errors=(ArgumentError, NotFoundError))
    async def search_drink(
        self,
        interaction: discord.Interaction,
        name: Optional[str],
        ingredient_name: Optional[str],
        glass_name: Optional[str],
        full: bool = False,
    ) -> None:
        if isinstance(name, str):
            data = await self.bot.database.get_drink(name)

            if not data:
                raise NotFoundError(f'No drinks with ID or name {name!r} been found.')

            glass = await self.bot.database.get_glass_by_id(data.glass)

            if not glass:
                raise IndexError(f'Failed to get glass from database.')

            ingredient_data = await self.bot.database.get_drink_ingredients(data.id)
            embed = drink_embed(data, glass, ingredient_data, full=full)

            await interaction.followup.send(embed=embed)

        elif isinstance(ingredient_name, str) or isinstance(glass_name, str):
            ingredients: list[int] = []

            if ingredient_name:
                for i in ingredient_name.split(','):
                    if not i:
                        continue

                    ingredient = await self.bot.database.get_ingredient(i)

                    if not ingredient:
                        raise NotFoundError(f'No ingredients with ID or name {i!r} been found.')

                    ingredients.append(ingredient.id)

            if glass_name:
                glass = await self.bot.database.get_glass(glass_name)
                if not glass:
                    raise NotFoundError(f'No glasses with ID or name {glass_name!r} been found.')
                glass_id = glass.id
            else:
                glass_id = None

            drinks = await self.bot.database.search_drinks(ingredients, glass_id)

            embeds = search_result_embed(drinks, full=full)
            view = PaginationView(embeds, interaction.user)

            message = await interaction.followup.send(embed=embeds[0], view=view, wait=True)
            view.message = message

        else:
            raise ArgumentError('Either `name` or `ingredient` have to be specified.')

    @app_commands.describe(
        name='Name or ID of ingredient.',
        full='Display full info about ingredient, defaults to False.',
    )
    @app_commands.command(name='ingredient', description='Search for ingredient.')
    @cog_logging_wrapper(logger=logger)
    async def search_ingredient(self, interaction: discord.Interaction, name: str, full: bool = False) -> None:
        data = await self.bot.database.get_ingredient(name)

        if data:
            embed = ingredient_embed(data, full=full)
            await interaction.followup.send(embed=embed)
        else:
            raise NotFoundError(f'No ingredients with ID or name {name!r} been found.')


async def setup(bot: 'CustomBot'):
    await bot.add_cog(
        Search(bot),
        guild=discord.Object(id=config.SERVER) if config.SERVER else None,
    )
