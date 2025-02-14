import logging
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

if TYPE_CHECKING:
    from main import CustomBot

logger = logging.getLogger(__name__)


class Utils(commands.Cog):
    def __init__(self, bot: 'CustomBot'):
        self.bot: 'CustomBot' = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{__name__} - loaded.')

    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx: commands.Context['CustomBot']) -> None:
        fmt = await ctx.bot.tree.sync(guild=ctx.guild)
        await ctx.send(f"Synced {len(fmt)} commands to current guild")
        return

    @commands.command()
    @commands.is_owner()
    async def globalsync(self, ctx: commands.Context['CustomBot']) -> None:
        fmt = await ctx.bot.tree.sync()
        await ctx.send(f"Synced {len(fmt)} commands")
        return

    @commands.command()
    @commands.is_owner()
    async def logs(self, ctx: commands.Context['CustomBot']) -> None:
        log = discord.File("discord.log")
        await ctx.send(file=log)


async def setup(bot: 'CustomBot'):
    await bot.add_cog(Utils(bot))
