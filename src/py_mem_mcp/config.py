"""Configuration management for py-mem-mcp.

Loads environment variables from a .env file and provides helpers
for accessing required configuration values.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the project root (three levels up from this file)
_env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(_env_path)


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
