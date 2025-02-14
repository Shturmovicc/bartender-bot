import asyncio
import logging
import logging.handlers
import os
from pathlib import Path
from typing import Any

import discord
from aiohttp import ClientSession, CookieJar
from discord.ext import commands

import config

logger = logging.getLogger(__name__)


class CustomBot(commands.Bot):
    def __init__(self, *args: Any, web_session: ClientSession, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.web_session = web_session

    async def setup_hook(self) -> None:
        for file in os.listdir(Path(__file__).parent / Path('cogs')):
            if file.endswith('.py'):
                await self.load_extension(f'cogs.{file[:-3]}')

    async def on_ready(self):
        assert self.user
        print(f'Logged in as {self.user} (ID: {self.user.id})')


async def main():
    intents = discord.Intents.all()

    logging.getLogger('discord').setLevel(logging.INFO)
    logging.getLogger('discord.http').setLevel(logging.INFO)

    handler = logging.handlers.RotatingFileHandler(
        filename='discord.log',
        encoding='utf-8',
        maxBytes=5 * 1024 * 1024,  # 5 MiB
        backupCount=5,
    )
    dt_fmt = '%Y-%m-%d %H:%M:%S'
    log_fmt = '[{asctime}] [{levelname:<8}] {name}: {message}'
    formatter = logging.Formatter(log_fmt, dt_fmt, style='{')
    handler.setFormatter(formatter)

    logging.basicConfig(format=log_fmt, datefmt=dt_fmt, style='{', handlers=[handler], level=logging.INFO)

    cookies = CookieJar()

    async with ClientSession(cookie_jar=cookies) as web_session:
        async with CustomBot(
            command_prefix='!',
            intents=intents,
            help_command=None,
            web_session=web_session,
        ) as bot:
            await bot.start(config.TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
