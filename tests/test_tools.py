"""Unit tests for MCP tool registration and basic logic."""

import asyncio
import os
from unittest.mock import AsyncMock, patch

import pytest

from py_mem_mcp.bundesland import BundeslandRegistry
from py_mem_mcp.graphs import GraphRegistry
from py_mem_mcp.sparql import SparqlBinding, SparqlClient, SparqlResults
from py_mem_mcp.tools.listing import ListingTools
from py_mem_mcp.tools.query import QueryTools
from py_mem_mcp.tools.search import SearchTools


_REQUIRED_VARS = {
    "GRAPH_ONTOLOGY": "https://ontology.example.com/",
    "GRAPH_SCHULART": "https://schulart.example.com/",
    "GRAPH_SCHULFACH": "https://schulfach.example.com/",
}


@pytest.fixture
def graph_env(monkeypatch):
    for key, value in _REQUIRED_VARS.items():
        monkeypatch.setenv(key, value)
    for key in list(os.environ):
        if key.startswith("GRAPH_STATE_"):
            monkeypatch.delenv(key, raising=False)
    yield


@pytest.fixture
def components(graph_env):
    graphs = GraphRegistry()
    sparql = SparqlClient("https://sparql.example.com/sparql")
    bl_reg = BundeslandRegistry()
    return sparql, graphs, bl_reg


def _mock_results(vars_: list[str], rows: list[list[str]]) -> SparqlResults:
    bindings = [
        {v: SparqlBinding(type="literal", value=row[i]) for i, v in enumerate(vars_)}
        for row in rows
    ]
    return SparqlResults(vars=vars_, bindings=bindings)


class TestQueryTools:
    def test_registration_succeeds(self, components):
        from fastmcp import FastMCP
        sparql, graphs, _ = components
        mcp = FastMCP("test")
        QueryTools(sparql, graphs).register(mcp)

    @pytest.mark.asyncio
    async def test_sparql_query_tool_calls_client(self, components):
        from fastmcp import FastMCP
        sparql, graphs, _ = components
        mcp = FastMCP("test")
        QueryTools(sparql, graphs).register(mcp)

        mock_results = _mock_results(["s"], [["value1"]])
        sparql.query = AsyncMock(return_value=mock_results)

        tools = await mcp.get_tools()
        assert "sparql_query" in tools
        result, _ = await mcp._call_tool_mcp("sparql_query", {"query": "SELECT * WHERE { ?s ?p ?o }"})
        sparql.query.assert_called_once()
        assert "value1" in result[0].text


class TestListingTools:
    def test_registration_succeeds(self, components):
        from fastmcp import FastMCP
        sparql, graphs, bl_reg = components
        mcp = FastMCP("test")
        ListingTools(sparql, graphs, bl_reg).register(mcp)

    @pytest.mark.asyncio
    async def test_list_bundeslaender_registered(self, components):
        from fastmcp import FastMCP
        sparql, graphs, bl_reg = components
        mcp = FastMCP("test")
        ListingTools(sparql, graphs, bl_reg).register(mcp)
        tools = await mcp.get_tools()
        assert "list_bundeslaender" in tools
        assert "list_schulfaecher" in tools
        assert "list_schularten" in tools

    @pytest.mark.asyncio
    async def test_list_bundeslaender_returns_formatted(self, components):
        from fastmcp import FastMCP
        sparql, graphs, bl_reg = components
        mcp = FastMCP("test")
        ListingTools(sparql, graphs, bl_reg).register(mcp)

        mock_results = _mock_results(["uri", "label"], [
            ["https://example.com/BY", "Bayern"],
        ])
        sparql.query = AsyncMock(return_value=mock_results)

        result, _ = await mcp._call_tool_mcp("list_bundeslaender", {})
        assert "Bayern" in result[0].text


class TestSearchTools:
    @pytest.mark.asyncio
    async def test_search_requires_bundesland_with_schulfach(self, components):
        from fastmcp import FastMCP
        from fastmcp.exceptions import ToolError
        sparql, graphs, bl_reg = components
        mcp = FastMCP("test")
        SearchTools(sparql, graphs, bl_reg).register(mcp)

        # Calling search with schulfach but no bundesland should raise a ToolError
        with pytest.raises(ToolError, match="Bundesland is required"):
            await mcp._call_tool_mcp("search", {"query": "Fisch", "schulfach": "Biologie"})

    @pytest.mark.asyncio
    async def test_search_returns_no_results_message(self, components):
        from fastmcp import FastMCP
        sparql, graphs, bl_reg = components
        mcp = FastMCP("test")
        SearchTools(sparql, graphs, bl_reg).register(mcp)

        sparql.query = AsyncMock(return_value=SparqlResults(vars=["s", "label"], bindings=[]))

        result, _ = await mcp._call_tool_mcp("search", {"query": "Fisch"})
        assert 'No results found for "Fisch"' in result[0].text
