"""Configuration management for py-mem-mcp.

Loads environment variables from a .env file and provides helpers
for accessing required configuration values.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

print("config")
# Load .env from the project root -- if executed should be pwd
_env_path = Path.cwd() / ".env"
if not _env_path.exists():
    raise FileNotFoundError(f"Missing .env file: {_env_path}")
load_dotenv(_env_path)
print(os.environ)


def require_env(name: str) -> str:
    """Return the value of a required environment variable.

    Raises:
        EnvironmentError: If the variable is not set or empty.
    """
    value = os.environ.get(name)
    if not value:
        raise EnvironmentError(
            f"Missing required environment variable: {name}. "
            "See .env.example for reference."
        )
    return value
