import random
from enum import StrEnum
from typing import Optional


class FruitEmojis(StrEnum):
    GREEN_APPLE = '\uD83C\uDF4F'
    RED_APPLE = '\uD83C\uDF4E'
    PEAR = '\uD83C\uDF50'
    TANGERINE = '\uD83C\uDF4A'
    LEMON = '\uD83C\uDF4B'
    BANANA = '\uD83C\uDF4C'
    WATERMELON = '\uD83C\uDF49'
    GRAPES = '\uD83C\uDF47'
    STRAWBERRY = '\uD83C\uDF53'
    MELON = '\uD83C\uDF48'
    CHERRIES = '\uD83C\uDF52'
    PEACH = '\uD83C\uDF51'
    MANGO = '\uD83E\uDD6D'
    PINEAPPLE = '\uD83C\uDF4D'
    COCONUT = '\uD83E\uDD65'
    KIWI = '\uD83E\uDD5D'


class DrinkEmojis(StrEnum):
    WINE_GLASS = '\uD83C\uDF77'
    TUMBLER_GLASS = '\uD83E\uDD43'
    COCKTAIL = '\uD83C\uDF78'
    TROPICAL_DRINK = '\uD83C\uDF79'


class Emojis(StrEnum):
    ZERO_WIDTH_SPACE = '\u200B'

    ARROW_LEFT = '\u2B05'
    ARROW_RIGHT = '\u27A1'
    BLACK_SMALL_SQUARE = '\u25AA'

    MAGNIFYING_GLASS = '\uD83D\uDD0D'
    BACKPACK = '\uD83C\uDF92'

    CROSS_MARK = '\u274C'
    CHECK_MARK = '\u2705'
    HANDSHAKE = '\uD83E\uDD1D'


def random_fruit_emoji(seed: Optional[str] = None) -> str:
    random.seed(seed)
    return random.choice(list(FruitEmojis))


def random_drink_emoji(seed: Optional[str] = None) -> str:
    random.seed(seed)
    return random.choice(list(DrinkEmojis))
