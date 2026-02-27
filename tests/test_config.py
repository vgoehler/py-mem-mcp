"""Unit tests for py_mem_mcp.config."""

import os

import pytest

from py_mem_mcp.config import require_env


def test_require_env_returns_value(monkeypatch):
    monkeypatch.setenv("TEST_REQUIRE_VAR", "hello")
    assert require_env("TEST_REQUIRE_VAR") == "hello"


def test_require_env_raises_when_missing(monkeypatch):
    monkeypatch.delenv("MISSING_VAR", raising=False)
    with pytest.raises(EnvironmentError, match="MISSING_VAR"):
        require_env("MISSING_VAR")


def test_require_env_raises_when_empty(monkeypatch):
    monkeypatch.setenv("EMPTY_VAR", "")
    with pytest.raises(EnvironmentError, match="EMPTY_VAR"):
        require_env("EMPTY_VAR")
