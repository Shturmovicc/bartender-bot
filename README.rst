Bartender Bot
=============

Discord bot with drink crafting system.

Features
--------

- Random drinks or ingredients from database.
- Search for drinks and ingredients in database.
- Drink crafting from ingredients.
- Ingredients, drinks and glasses inventory.
- Random rolls system with ingredients, glasses and drinks.

Commands
--------

Currectly available bot app (slash) commands:

* **random**

  * **drink**: Display random drink from database.

    * | ``full``: ``Optional[bool]``
      | Display full info about drink, defaults to ``False``.

  * **ingredient**: Display random ingredient from database.

    * | ``full``: ``Optional[bool]``
      | Display full info about ingredient, defaults to ``False``.

* **search**

  * **drink**: Search for drink in database.

    * | ``name``: ``string | number``
      | Name or ID of drink.
    * | ``ingredient``: ``string | number``
      | Name or ID of ingredients separated by comma that will be used in search.
    * | ``glass``: ``string | number``
      | Name or ID of glass that will be used in search.
    * | ``full``: ``Optional[bool]``
      | Display full info about drink, defaults to ``False``.

  * **ingredient**: Search for ingredient in database.

    * | ``name``: ``string | number``
      | Name or ID of ingredient.
    * | ``full``: ``Optional[bool]``
      | Display full info about ingredient, defaults to ``False``.

* **inventory**

  * **drinks**: Shows drinks inventory.

    * | ``user``: ``Optional[discord.User]``
      | User to show inventory of, defaults to self.

  * **glasses**: Shows glasses inventory.

    * | ``user``: ``Optional[discord.User]``
      | User to show inventory of, defaults to self.

  * **ingredients**: Shows ingredients inventory.

    * | ``user``: ``Optional[discord.User]``
      | User to show inventory of, defaults to self.

* **craft**: Craft drink from ingredients you have, if ``name`` not specified shows list of drinks you can make.

  * | ``name``: ``string | number``
    | Name or ID of drink you want to craft.

* | **roll**: Roll for random drink, glass or ingredient. After that it's added to your inventory.
  | 90% chance for ingredient.
  | 9% chance for glass.
  | 1% chance for drink.

* **trade**: Trade with other user using your drinks, glasses or ingredients.

  * | ``user``: ``discord.User``
    | User to trade with.
  * | ``offer``: ``string``
    | Items to offer other user, should be in format of ``{type}:{name or id}[:amount]`` example: ``d:12345:10, glass:12``
  * | ``request``: ``string``
    | Items to request from other user, should be in format of ``{type}:{name or id}[:amount]`` example: ``ingredient:12345:10, g:5``

License
-------

MIT, see LICENSE for details.
