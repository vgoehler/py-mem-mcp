"""Configuration management for py-mem-mcp.

Loads environment variables from a .env file and provides helpers
for accessing required configuration values.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


def config_vars_sanity_check(env_path: Path):
    if os.environ.get("GRAPH_ONTOLOGY") is None and not env_path.exists():
        raise FileNotFoundError(f"Missing .env file: {env_path} or Environment variables.")

def init_env_vars():
    # Load .env from the project root -- if executed should be pwd
    env_path = Path.cwd() / ".env"
    config_vars_sanity_check(env_path)
    load_dotenv(env_path)

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
