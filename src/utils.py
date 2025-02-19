import functools
from logging import Logger
from typing import Any, Callable

import discord
from discord.ext import commands


def cog_logging_wrapper(*, logger: Logger, skip_errors: tuple[type[Exception], ...] = ()):
    def decorator(func: Callable[..., Any]):
        @functools.wraps(func)
        async def wrapper(self: commands.Cog, interaction: discord.Interaction, *args: Any, **kwargs: Any):
            assert interaction.command

            await interaction.response.defer()

            logger.info(f'{interaction.user.name}:{interaction.user.id} used {interaction.command.name}')
            try:
                await func(self, interaction, *args, **kwargs)
            except skip_errors as error:
                msg = f'{error.__class__.__qualname__}: {error}'
                await interaction.followup.send(f'```{msg}```')
            except Exception as error:
                logger.exception(f'{error.__class__.__name__}: {error}')
                await interaction.followup.send(f'```{error.__class__.__qualname__}: {error}```')

        return wrapper

    return decorator
