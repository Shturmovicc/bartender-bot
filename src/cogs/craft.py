import logging
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Optional

import discord
from discord import Member, User, app_commands
from discord.ext import commands

import config
from database.models import UserGlass, UserIngredient, UserSetItemSignature
from embeds import PaginationView, available_crafts_embed, drink_embed, search_result_embed
from exceptions import MissingGlassError, MissingIngredientError, NotFoundError
from utils import cog_logging_wrapper

if TYPE_CHECKING:
    from main import CustomBot

logger = logging.getLogger(__name__)


class ConfirmCraftView(discord.ui.View):
    message: discord.Message

    def __init__(
        self,
        user: Member | User,
        confirm_callback: Callable[[], Awaitable[float]],
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)

        self.user = user
        self.confirm_callback = confirm_callback

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button['ConfirmCraftView']):
        await interaction.response.defer(ephemeral=True, thinking=True)
        await self.message.edit(view=None)
        amount = await self.confirm_callback()
        await interaction.followup.send(f'`Successfully crafted drink! Now you have {amount}`.', ephemeral=True)

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button['ConfirmCraftView']):
        await interaction.response.edit_message(view=None)

    async def on_timeout(self) -> None:
        await self.message.edit(view=None)

    async def interaction_check(self, interaction: discord.Interaction[discord.Client]) -> bool:
        return interaction.user.id == self.user.id

    async def on_error(self, interaction: discord.Interaction, error: Exception, item: discord.ui.Item[Any]):
        if not isinstance(error, (MissingGlassError, MissingIngredientError)):
            logger.exception(f'{error.__class__.__name__}: {error}')
        await interaction.followup.send(f'```{error.__class__.__qualname__}: {error}```', ephemeral=True)


class Craft(commands.Cog):
    def __init__(self, bot: 'CustomBot'):
        self.bot: 'CustomBot' = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{__name__} - loaded.')

    @app_commands.describe(name='Name or ID of drink to craft.')
    @app_commands.command(name='craft', description='Craft drink from ingredients you have.')
    @cog_logging_wrapper(logger=logger, skip_errors=(MissingGlassError, MissingIngredientError, NotFoundError))
    async def craft_drink(self, interaction: discord.Interaction, name: Optional[str]) -> None:
        if name is None:
            items = await self.bot.database.get_available_crafts(interaction.user.id)

            embeds = available_crafts_embed(interaction.user, items)

            view = PaginationView(embeds, interaction.user, timeout=300)
            message = await interaction.followup.send(embed=embeds[0], view=view, wait=True)
            view.message = message
            return

        drink = await self.bot.database.get_drink(name)
        if not drink:
            raise NotFoundError('Drink not found.')
        elif isinstance(drink, list):
            msg = '`Found more than 1 drink with this name.`\n`Try using full name or ID.`'
            embeds = search_result_embed(drink, full=False)
            view = PaginationView(embeds, interaction.user, timeout=300)
            message = await interaction.followup.send(msg, embed=embeds[0], view=view, wait=True)
            view.message = message
            return

        glass = await self.bot.database.get_glass_by_id(drink.glass)
        assert glass

        ingredients = await self.bot.database.get_drink_ingredients(drink.id)
        ingredient_ids = {i.id for i in ingredients}

        async def check() -> tuple[float, UserGlass, dict[int, UserIngredient]]:
            user_drinks = await self.bot.database.get_user_drinks(interaction.user.id)
            user_glasses = await self.bot.database.get_user_glasses(interaction.user.id)
            user_ingredients = await self.bot.database.get_user_ingredients(interaction.user.id)

            drink_exists = user_drinks.get(drink.id)
            glass_exists = user_glasses.get(drink.glass)
            ingredients_exist = {item.id: item for item in user_ingredients.values() if item.id in ingredient_ids}

            if drink_exists:
                amount = drink_exists.amount + 1
            else:
                amount = 1

            if not glass_exists:
                raise MissingGlassError('You are missing glass to make this drink!')

            if len(ingredients_exist) != len(ingredient_ids):
                msg = "\n".join([f'{i.name}' for i in ingredients if i.id not in ingredients_exist])
                raise MissingIngredientError(f'\n{msg}')

            return amount, glass_exists, ingredients_exist

        async def confirm_callback() -> float:
            amount, glass_exists, ingredients_exist = await check()

            async with self.bot.database:
                await self.bot.database.set_user_drinks(
                    UserSetItemSignature(interaction.user.id, drink.id, amount=amount),
                )

                await self.bot.database.set_user_glasses(
                    UserSetItemSignature(interaction.user.id, glass_exists.id, amount=glass_exists.amount - 1),
                )

                ingredient_set_items: list[UserSetItemSignature] = []
                for ingredient in ingredients_exist.values():
                    ingredient_amount = ingredient.amount - 1
                    ingredient_set_items.append(
                        UserSetItemSignature(interaction.user.id, ingredient.id, ingredient_amount),
                    )
                await self.bot.database.set_user_ingredients(*ingredient_set_items)

            return amount

        await check()

        view = ConfirmCraftView(interaction.user, confirm_callback, timeout=300)
        embed = drink_embed(drink, glass, ingredients)

        msg = '`Are you sure that you want to craft this drink?`'
        message = await interaction.followup.send(msg, view=view, embed=embed, wait=True)
        view.message = message


async def setup(bot: 'CustomBot'):
    await bot.add_cog(
        Craft(bot),
        guild=discord.Object(id=config.SERVER) if config.SERVER else None,
    )
