class BotException(Exception):
    pass


class NotFoundError(BotException):
    pass


class ArgumentError(BotException):
    pass


class MissingGlassError(BotException):
    pass


class MissingIngredientError(BotException):
    __qualname__ = f'Missing following ingredients'
