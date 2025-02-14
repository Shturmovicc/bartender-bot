import os

TOKEN = os.getenv('BOT_TOKEN', '')

if not TOKEN:
    raise ValueError('`BOT_TOKEN` environment variable is not set.')
