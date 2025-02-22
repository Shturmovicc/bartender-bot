import copy
import logging
import re
from dataclasses import asdict
from itertools import zip_longest
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Optional, Self

import discord
from discord import Member, User, app_commands
from discord.ext import commands

import config
from database.models import Drink, Glass, Ingredient, UserDrink, UserGlass, UserIngredient, UserInventory
from embeds import trade_offer_embed
from emojis import Emojis
from exceptions import ArgumentError, NotFoundError
from typedefs import ItemType
from utils import cog_logging_wrapper, reverse_dict

if TYPE_CHECKING:
    from main import CustomBot

logger = logging.getLogger(__name__)


ParsedData = dict[ItemType, list[tuple[str, int]]]

PARSE_REGEXP = re.compile(r'(?P<type>[A-Za-z]+)[: ]+(?P<name>[\w ]+)[:]*(?P<amount>\d+)*')

VALID_TYPES = reverse_dict(
    {
        ItemType.DRINK: ('d', 'drink'),
        ItemType.GLASS: ('g', 'glass'),
        ItemType.INGREDIENT: ('i', 'ingredient'),
    }
)


def parse_items(input_string: str) -> ParsedData:
    matches = PARSE_REGEXP.finditer(input_string)

    out: ParsedData = {
        ItemType.INGREDIENT: [],
        ItemType.DRINK: [],
        ItemType.GLASS: [],
    }

    for match in matches:
        type = match['type']
        name = match['name']
        amount = int(match['amount'] or '1')
        if type in VALID_TYPES and amount > 0:
            out[VALID_TYPES[type]].append((name, amount))

    return out


class AcceptView(discord.ui.View):
    message: discord.Message

    def __init__(
        self,
        *args: Any,
        user: Member | User,
        target: Member | User,
        callback: Callable[[], Awaitable[Any]],
        embed: discord.Embed,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.user = user
        self.target = target
        self.callback = callback
        self.embed = embed

    @discord.ui.button(label='Accept', style=discord.ButtonStyle.green)
    async def accept_callback(self, interaction: discord.Interaction, button: discord.ui.Button[Self]) -> None:
        if interaction.user.id != self.target.id:
            return

        await self.disable_buttons()
        await interaction.response.defer()

        await self.callback()

        self.embed.color = discord.Color.from_rgb(13, 189, 16)
        self.embed.title = f'{Emojis.CHECK_MARK} Trade has been accepted.'

        await interaction.followup.edit_message(self.message.id, view=None, embed=self.embed)

    @discord.ui.button(label='Decline', style=discord.ButtonStyle.red)
    async def decline_callback(self, interaction: discord.Interaction, button: discord.ui.Button[Self]) -> None:
        self.embed.color = discord.Color.from_rgb(222, 18, 18)
        self.embed.title = f'{Emojis.CROSS_MARK} Trade has been cancelled by {interaction.user.display_name}.'

        await interaction.response.edit_message(view=None, embed=self.embed)

    async def disable_buttons(self) -> None:
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True

        await self.message.edit(view=self)

    async def on_timeout(self) -> None:
        await self.message.edit(view=None)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user.id or interaction.user.id == self.target.id

    async def on_error(self, interaction: discord.Interaction, error: Exception, item: discord.ui.Item[Any]):
        if not isinstance(error, (ArgumentError)):
            logger.exception(f'{error.__class__.__name__}: {error}')
        await interaction.followup.send(f'```{error.__class__.__qualname__}: {error}```', ephemeral=True)


class Trade(commands.Cog):
    def __init__(self, bot: 'CustomBot'):
        self.bot: 'CustomBot' = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{__name__} - loaded.')

    async def get_items(self, data: ParsedData) -> UserInventory:
        items = UserInventory({}, {}, {})

        for key, values in data.items():
            for value in values:
                item = await self.bot.database.get_item(key, value[0])

                if item is None:
                    raise NotFoundError(f'{key.title()} with name or ID {value[0]} was not found.')
                elif isinstance(item, list):
                    item = item[0]

                if isinstance(item, Drink):
                    items.drinks[item.id] = UserDrink(**asdict(item), amount=value[1])
                elif isinstance(item, Glass):
                    items.glasses[item.id] = UserGlass(**asdict(item), amount=value[1])
                elif isinstance(item, Ingredient):
                    items.ingredients[item.id] = UserIngredient(**asdict(item), amount=value[1])

        return items

    def has_items(
        self,
        inventory: UserInventory,
        items: UserInventory,
    ):
        for inventory_items, item_list in zip(inventory, items):
            for item in item_list.values():
                if item.id in inventory_items:
                    if inventory_items[item.id].amount < item.amount:
                        raise ValueError(item.name)
                else:
                    raise ValueError(item.name)

    def get_different_items(
        self,
        inventory: UserInventory,
        *,
        add: Optional[UserInventory] = None,
        remove: Optional[UserInventory] = None,
    ):
        # This whole function smells really bad but I don't know how to do it dynamically better.
        diff = UserInventory({}, {}, {})
        # Assuming remove_items all present in items
        for items, diff_items, add_items, remove_items in zip_longest(inventory, diff, add or (), remove or ()):
            if add_items:
                for id, item in add_items.items():
                    if id in diff_items:
                        item_copy = diff_items[id]
                    elif id in items:
                        item_copy = copy.copy(items[id])
                    else:
                        item_copy = copy.copy(item)
                        item_copy.amount = 0

                    item_copy.amount += item.amount  # pyright: ignore[reportAttributeAccessIssue] It'll be always same type.
                    diff_items[id] = item_copy  # pyright: ignore[reportArgumentType] It'll be always same type.

            if remove_items:
                for id, item in remove_items.items():
                    if id in diff_items:
                        item_copy = diff_items[id]
                    else:
                        item_copy = copy.copy(items[id])

                    item_copy.amount -= item.amount  # pyright: ignore[reportAttributeAccessIssue] It'll be always same type.
                    diff_items[id] = item_copy  # pyright: ignore[reportArgumentType] It'll be always same type.

        return diff

    @app_commands.describe(
        target='User to trade with.',
        offer_string='Items to offer other user, should be in format of {type}:{name or id}[:amount] example: d:12345:10, glass:12',
        request_string='Items to request from other user, should be in format of {type}:{name or id}[:amount] example: ingredient:12345:10, g:5',
    )
    @app_commands.rename(target='user', offer_string='offer', request_string='request')
    @app_commands.command(name='trade', description='Trade with other user using your drinks, glasses or ingredients.')
    @cog_logging_wrapper(logger=logger, skip_errors=(ArgumentError, NotFoundError))
    async def trade(self, interaction: discord.Interaction, target: discord.User, offer_string: str, request_string: str):
        if interaction.user.id == target.id:
            raise ArgumentError(f'Cannot trade with self.')
        elif target.bot:
            raise ArgumentError(f'Cannot trade with bot.')

        parsed_offer = parse_items(offer_string)
        parsed_request = parse_items(request_string)

        offer = await self.get_items(parsed_offer)
        request = await self.get_items(parsed_request)

        if not any(values for values in offer) and not any(values for values in request):
            raise ArgumentError('Unable to parse offer and request.')

        async def check() -> tuple[UserInventory, UserInventory]:
            user_inventory = await self.bot.database.get_user_inventory(interaction.user.id)
            target_inventory = await self.bot.database.get_user_inventory(target.id)

            try:
                self.has_items(user_inventory, offer)
            except ValueError as error:
                raise ArgumentError(f'You don\'t have enough of {error} to trade.')
            try:
                self.has_items(target_inventory, request)
            except ValueError as error:
                raise ArgumentError(f'Target doesn\'t have enough of {error} to trade.')

            return user_inventory, target_inventory

        async def transfer() -> None:
            user_inventory, target_inventory = await check()

            user_diff = self.get_different_items(user_inventory, add=request, remove=offer)
            target_diff = self.get_different_items(target_inventory, add=offer, remove=request)

            async with self.bot.database:
                await self.bot.database.set_user_inventory(interaction.user.id, user_diff)
                await self.bot.database.set_user_inventory(target.id, target_diff)

        await check()

        embed = trade_offer_embed(interaction.user, offer=offer, request=request)
        view = AcceptView(user=interaction.user, target=target, callback=transfer, embed=embed, timeout=300)

        message = await interaction.followup.send(
            f'Hey, <@{target.id}>\nYou received trade offer from `{interaction.user.display_name}`',
            embed=embed,
            view=view,
            wait=True,
        )
        view.message = message


async def setup(bot: 'CustomBot'):
    await bot.add_cog(
        Trade(bot),
        guild=discord.Object(id=config.SERVER) if config.SERVER else None,
    )
