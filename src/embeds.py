import math
import random
from typing import Any, Literal, Optional, Sequence

import discord
from discord import Color, Embed, Member, User
from yarl import URL

from database.models import Drink, DrinkIngredient, Glass, Ingredient, UserDrink, UserGlass, UserIngredient


class PaginationView(discord.ui.View):
    message: discord.Message

    def __init__(
        self,
        pages: Sequence[discord.Embed],
        user: discord.Member | discord.User,
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)

        self.pages = pages
        self.index = 0

        self.user = user

        if len(self.pages) <= 1:
            for button in self.children:
                self.remove_item(button)

    @discord.ui.button(emoji='\u2B05', style=discord.ButtonStyle.blurple)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button['PaginationView']):
        self.index -= 1
        if self.index < 0:
            self.index = len(self.pages) - 1

        await self.set_page(interaction, self.index)

    @discord.ui.button(emoji='\u25aa', style=discord.ButtonStyle.grey)
    async def placeholder(self, interaction: discord.Interaction, button: discord.ui.Button['PaginationView']):
        await interaction.response.pong()

    @discord.ui.button(emoji='\u27A1', style=discord.ButtonStyle.blurple)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button['PaginationView']):
        self.index += 1
        if self.index + 1 > len(self.pages):
            self.index = 0

        await self.set_page(interaction, self.index)

    async def set_page(self, interaction: discord.Interaction, index: int) -> None:
        page = self.pages[index]
        await interaction.response.edit_message(embed=page, view=self)

    async def on_timeout(self) -> None:
        await self.message.edit(view=None)

    async def interaction_check(self, interaction: discord.Interaction[discord.Client]) -> bool:
        return interaction.user.id == self.user.id


def _random_color(max_total: int = 400, seed: Optional[str] = None) -> Color:
    random.seed(seed)
    r = random.randint(0, 255)
    g = random.randint(0, min(max_total - r, 255))
    b = random.randint(0, min(max_total - r - g, 255))

    return Color.from_rgb(*random.sample([r, g, b], 3))


def _shorten_text(string: str, max_length: int = 100, split: bool = True) -> str:
    if split:
        string = (string.split('\n'))[0]

    if len(string) > max_length:
        string = string[:max_length] + '...'

    return string


def _paginate(
    base: Embed,
    items: Sequence[tuple[str, str]],
    style: Literal['description', 'fields'] = 'description',
    max_page_items: int = 25,
) -> list[Embed]:
    embeds: list[Embed] = []

    pages = max(math.ceil(len(items) / max_page_items), 1)
    for i in range(pages):
        embed = base.copy()

        leftover_items = len(items) - i * max_page_items

        if style == 'description':
            description: list[str] = []
            for row in range(max(min(leftover_items, max_page_items), 0)):
                item = items[i * max_page_items + row]
                if item[0]:
                    description.append(f'**{item[0]}**')
                if item[1]:
                    description.append(f'{item[1]}')
            embed.description = '\n'.join(description)
        elif style == 'fields':
            for row in range(max(min(leftover_items, max_page_items), 0)):
                item = items[i * max_page_items + row]
                embed.add_field(name=item[0], value=item[1], inline=False)

        if pages > 1:
            footer = f'Page {i+1}/{pages}'
            if base.footer.text:
                footer += f' | {base.footer.text}'
        else:
            footer = base.footer.text

        embed.set_footer(text=footer, icon_url=base.footer.icon_url)

        embeds.append(embed)

    return embeds


def _strip_amount(amount: int | float) -> int | float:
    return int(amount) if isinstance(amount, float) and amount.is_integer() else amount


def _ingredient_info(item: Ingredient, *, delimiter: str = '\n', prefix: str = '') -> str:
    return f'{delimiter}'.join(
        [
            f'{prefix}ID: {item.id}',
            f'{prefix}Type: {item.type}',
            f'{prefix}Alcohol: {item.alcohol}',
        ]
    )


def _ingredient_image_url(item: Ingredient) -> URL:
    return URL('https://www.thecocktaildb.com/images/ingredients') / f'{item.name}.png'


def _drink_info(item: Drink, *, delimiter: str = '\n', prefix: str = '') -> str:
    return f'{delimiter}'.join(
        [
            f'{prefix}ID: {item.id}',
            f'{prefix}Category: {item.category}',
            f'{prefix}Alcoholic: {item.alcoholic}',
        ]
    )


def drink_embed(item: Drink, glass: Glass, ingredients: list[DrinkIngredient], full: bool = False) -> Embed:
    embed = Embed(title=item.name, color=_random_color(seed=item.name))
    embed.set_image(url=item.thumbnail)
    embed.set_footer(text=_drink_info(item, delimiter=' | '))

    embed.add_field(name='Glass:', value=glass.name, inline=False)
    embed.add_field(name='Ingredients:', value='\n'.join([f'\\- {i.measure} {i.name}' for i in ingredients]))

    if full:
        if item.tags:
            embed.add_field(name='Tags:', value=item.tags.replace(',', '\n'), inline=False)
        if item.instructions:
            text = _shorten_text(item.instructions, 1020, False)
            embed.add_field(name='Instructions:', value=text, inline=False)

    return embed


def glass_embed(item: Glass) -> Embed:
    embed = Embed(title=item.name, color=_random_color(seed=item.name))
    embed.set_footer(text=f'ID: {item.id}')

    return embed


def ingredient_embed(item: Ingredient, style: Literal['thumbnail', 'image'] = 'thumbnail', full: bool = False) -> Embed:
    description = _shorten_text(item.description, 500) if item.description and not full else item.description

    embed = Embed(
        title=item.name,
        description=_shorten_text(description, 4090, False) if description else description,
        color=_random_color(seed=item.name),
    )

    if style == 'thumbnail':
        embed.set_thumbnail(url=_ingredient_image_url(item))
    elif style == 'image':
        embed.set_image(url=_ingredient_image_url(item))

    embed.set_footer(text=_ingredient_info(item, delimiter=' | '))

    return embed


def _base_inventory_embed(target: Member | User, type: str) -> Embed:
    embed = Embed(title=f'{target.display_name}\'s {type} inventory:')
    embed.set_author(name=target.name, icon_url=target.display_avatar)
    embed.set_footer(text=f'ID: {target.id}')

    return embed


def drink_inventory_embed(target: Member | User, items: list[UserDrink]) -> list[Embed]:
    base = _base_inventory_embed(target, 'drink')
    base.color = discord.Color.from_rgb(105, 8, 3)

    rows: list[tuple[str, str]] = []

    for item in items:
        amount = _strip_amount(item.amount)
        value = _drink_info(item, prefix="> ")
        rows.append((f'x{amount} {item.name}', value))

    return _paginate(base, rows, style='fields', max_page_items=5)


def glass_inventory_embed(target: Member | User, items: list[UserGlass]) -> list[Embed]:
    base = _base_inventory_embed(target, 'glass')
    base.color = discord.Color.from_rgb(22, 37, 148)

    rows: list[tuple[str, str]] = []
    for item in items:
        rows.append(('', f'- x{item.amount} {item.name}'))

    return _paginate(base, rows, max_page_items=10)


def ingredient_inventory_embed(target: Member | User, items: list[UserIngredient]) -> list[Embed]:
    base = _base_inventory_embed(target, 'ingredient')
    base.color = discord.Color.from_rgb(131, 11, 138)

    rows: list[tuple[str, str]] = []

    for item in items:
        amount = _strip_amount(item.amount)
        # value = [f'ID: {item.id}', f'Type: {item.type}', f'Alcohol: {item.alcohol}']

        rows.append(('', f'- x{amount} {item.name}'))  #'\n'.join(value)))

    return _paginate(base, rows, max_page_items=10)


def available_crafts_embed(user: Member | User, items: list[Drink]) -> list[Embed]:
    embed = Embed(
        title='Available drinks to craft:',
        description='Use `/craft name` to craft drink from your ingredients.',
        color=discord.Color.from_rgb(212, 58, 6),
    )
    embed.set_author(name=user.name, icon_url=user.display_avatar)
    embed.set_footer(text=f'ID: {user.id}')

    rows: list[tuple[str, str]] = []
    for item in items:
        value = _drink_info(item, prefix="> ")
        rows.append((f'\u25aa {item.name}', value))

    return _paginate(embed, rows, style='fields', max_page_items=5)


def search_result_embed(items: list[Drink] | list[Ingredient], *, full: bool = False) -> list[Embed]:
    embed = Embed(
        title='Search results:',
        color=discord.Color.from_rgb(18, 181, 105),
    )

    rows: list[tuple[str, str]] = []
    for item in items:
        name = f'\u25aa {item.name}'

        if isinstance(item, Drink) and full:
            value = _drink_info(item, prefix="> ")
        elif isinstance(item, Ingredient) and full:
            value = _ingredient_info(item, prefix="> ")
        else:
            name += f' ({item.id})'
            value = ''

        rows.append((name, value))

    return _paginate(embed, rows, style='fields', max_page_items=10 if not full else 5)
