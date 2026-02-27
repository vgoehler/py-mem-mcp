"""Unit tests for py_mem_mcp.graphs."""

import os

import pytest

from py_mem_mcp.graphs import GraphRegistry


_REQUIRED_VARS = {
    "GRAPH_ONTOLOGY": "https://ontology.example.com/",
    "GRAPH_SCHULART": "https://schulart.example.com/",
    "GRAPH_SCHULFACH": "https://schulfach.example.com/",
}


@pytest.fixture
def graph_env(monkeypatch):
    """Set required environment variables for GraphRegistry."""
    for key, value in _REQUIRED_VARS.items():
        monkeypatch.setenv(key, value)
    # Remove any stray GRAPH_STATE_ vars
    for key in list(os.environ):
        if key.startswith("GRAPH_STATE_"):
            monkeypatch.delenv(key, raising=False)
    yield


@pytest.fixture
def graph_env_with_states(monkeypatch, graph_env):
    monkeypatch.setenv("GRAPH_STATE_SN", "https://sn.example.com/")
    monkeypatch.setenv("GRAPH_STATE_BY", "https://by.example.com/")
    yield


class TestGraphRegistry:
    def test_infra_graphs_loaded(self, graph_env):
        reg = GraphRegistry()
        assert "https://ontology.example.com/" in reg.infra_graphs
        assert "https://schulart.example.com/" in reg.infra_graphs
        assert "https://schulfach.example.com/" in reg.infra_graphs

    def test_no_state_graphs_by_default(self, graph_env):
        reg = GraphRegistry()
        assert reg.state_graphs == {}

    def test_state_graphs_loaded(self, graph_env_with_states):
        reg = GraphRegistry()
        assert "SN" in reg.state_graphs
        assert reg.state_graphs["SN"] == "https://sn.example.com/"
        assert "BY" in reg.state_graphs

    def test_all_graphs_includes_infra_and_state(self, graph_env_with_states):
        reg = GraphRegistry()
        all_g = reg.all_graphs
        assert "https://ontology.example.com/" in all_g
        assert "https://sn.example.com/" in all_g

    def test_graphs_for_bundesland_with_state(self, graph_env_with_states):
        reg = GraphRegistry()
        bl_graphs = reg.graphs_for_bundesland("SN")
        assert "https://sn.example.com/" in bl_graphs
        assert "https://ontology.example.com/" in bl_graphs

    def test_graphs_for_bundesland_without_state(self, graph_env):
        reg = GraphRegistry()
        bl_graphs = reg.graphs_for_bundesland("BE")
        assert bl_graphs == reg.infra_graphs

    def test_from_clauses(self, graph_env):
        clauses = GraphRegistry.from_clauses(["https://a.example.com/", "https://b.example.com/"])
        assert "FROM <https://a.example.com/>" in clauses
        assert "FROM <https://b.example.com/>" in clauses

    def test_missing_required_var_raises(self, monkeypatch):
        monkeypatch.delenv("GRAPH_ONTOLOGY", raising=False)
        monkeypatch.setenv("GRAPH_SCHULART", "https://schulart.example.com/")
        monkeypatch.setenv("GRAPH_SCHULFACH", "https://schulfach.example.com/")
        with pytest.raises(EnvironmentError):
            GraphRegistry()
