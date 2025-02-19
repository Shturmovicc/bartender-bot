import logging
from typing import TYPE_CHECKING, Optional

import discord
from discord import app_commands
from discord.ext import commands

import config
from embeds import PaginationView, drink_inventory_embed, glass_inventory_embed, ingredient_inventory_embed
from utils import cog_logging_wrapper

if TYPE_CHECKING:
    from main import CustomBot

logger = logging.getLogger(__name__)


class Inventory(commands.GroupCog, group_name='inventory'):
    def __init__(self, bot: 'CustomBot'):
        self.bot: 'CustomBot' = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{__name__} - loaded.')

    @app_commands.describe(user='User to show inventory of, defaults to self.')
    @app_commands.command(name='drinks', description='Show inventory with drinks.')
    @cog_logging_wrapper(logger=logger)
    async def inventory_drinks(self, interaction: discord.Interaction, user: Optional[discord.User]) -> None:
        target = user or interaction.user

        items = await self.bot.database.get_user_drinks(target.id)
        embeds = drink_inventory_embed(target, items)

        view = PaginationView(embeds, interaction.user, timeout=300)
        message = await interaction.followup.send(embed=embeds[0], view=view, wait=True)
        view.message = message

    @app_commands.describe(user='User to show inventory of, defaults to self.')
    @app_commands.command(name='glasses', description='Show inventory with glasses.')
    @cog_logging_wrapper(logger=logger)
    async def inventory_glasses(self, interaction: discord.Interaction, user: Optional[discord.User]) -> None:
        target = user or interaction.user

        items = await self.bot.database.get_user_glasses(target.id)
        embeds = glass_inventory_embed(target, items)

        view = PaginationView(embeds, interaction.user, timeout=300)
        message = await interaction.followup.send(embed=embeds[0], view=view, wait=True)
        view.message = message

    @app_commands.describe(user='User to show inventory of, defaults to self.')
    @app_commands.command(name='ingredients', description='Show inventory with ingredients.')
    @cog_logging_wrapper(logger=logger)
    async def inventory_ingredients(self, interaction: discord.Interaction, user: Optional[discord.User]) -> None:
        target = user or interaction.user

        items = await self.bot.database.get_user_ingredients(target.id)
        embeds = ingredient_inventory_embed(target, items)

        view = PaginationView(embeds, interaction.user, timeout=300)
        message = await interaction.followup.send(embed=embeds[0], view=view, wait=True)
        view.message = message


async def setup(bot: 'CustomBot'):
    await bot.add_cog(
        Inventory(bot),
        guild=discord.Object(id=config.SERVER) if config.SERVER else None,
    )
