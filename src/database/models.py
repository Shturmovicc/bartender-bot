from dataclasses import dataclass
from typing import NamedTuple


@dataclass(slots=True)
class UserSetItemSignature:
    user_id: int
    item_id: int
    amount: float


@dataclass(slots=True)
class Drink:
    id: int
    name: str
    name_alternate: str | None
    tags: str | None
    category: str | None
    alcoholic: bool
    glass: int
    instructions: str | None
    thumbnail: str


@dataclass(slots=True)
class UserDrink(Drink):
    amount: float


@dataclass(slots=True)
class Glass:
    id: int
    name: str


@dataclass(slots=True)
class UserGlass(Glass):
    amount: int


@dataclass(slots=True)
class Ingredient:
    id: int
    name: str
    description: str | None
    type: str | None
    alcohol: bool


@dataclass(slots=True)
class DrinkIngredient(Ingredient):
    measure: str | None


@dataclass(slots=True)
class UserIngredient(Ingredient):
    amount: float


class UserInventory(NamedTuple):  # NamedTuple instead of dataclass for easier comparison.
    drinks: dict[int, UserDrink]
    glasses: dict[int, UserGlass]
    ingredients: dict[int, UserIngredient]
