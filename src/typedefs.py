from enum import StrEnum
from typing import TypeVar

KT = TypeVar('KT')
VT = TypeVar('VT')


class ItemType(StrEnum):
    DRINK = 'drink'
    GLASS = 'glass'
    INGREDIENT = 'ingredient'
