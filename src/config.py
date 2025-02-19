import os
from pathlib import Path

TOKEN: str = os.getenv('BOT_TOKEN', '')
SERVER: int | None = int(os.getenv('SERVER', '0')) or None
DB_PATH: Path = Path(__file__).parent / 'database.sqlite'

if not TOKEN:
    raise ValueError('`BOT_TOKEN` environment variable is not set.')
