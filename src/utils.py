import functools
from logging import Logger
from typing import Any, Callable, Sequence

import discord
from discord.ext import commands

from typedefs import KT, VT


def cog_logging_wrapper(*, logger: Logger, skip_errors: tuple[type[Exception], ...] = ()):
    def decorator(func: Callable[..., Any]):
        @functools.wraps(func)
        async def wrapper(self: commands.Cog, interaction: discord.Interaction, *args: Any, **kwargs: Any):
            assert interaction.command

            await interaction.response.defer()

            user = interaction.user
            logger.info(f'{user.name}:{user.id} used {interaction.command.qualified_name} with {kwargs}')
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


def reverse_dict(d: dict[KT, Sequence[VT]]) -> dict[VT, KT]:
    """Swaps dict `key` and `value` list to `value`:`key` for each `value` in `value` Sequence."""
    return {value: key for key, values in d.items() for value in values}
