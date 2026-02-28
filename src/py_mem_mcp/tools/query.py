"""Arbitrary SPARQL query tool for the MEM ontology MCP server."""

from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from ..graphs import GraphRegistry
from ..sparql import SparqlClient


class QueryTools:
    """Provides the ``sparql_query`` tool for executing raw SPARQL queries."""

    def __init__(self, sparql_client: SparqlClient, graph_registry: GraphRegistry) -> None:
        self.sparql = sparql_client
        self.graphs = graph_registry

    def register(self, mcp: FastMCP) -> None:
        """Register all query tools with the given FastMCP server instance."""
        sparql = self.sparql
        graphs = self.graphs

        graph_list = ", ".join(
            [f"<{g}>" for g in graphs.infra_graphs]
            + [f"{code}: <{g}>" for code, g in graphs.state_graphs.items()]
        )
        description = (
            "Execute a SPARQL query against the MEM ontology triple store. "
            "PREFIX lp: <https://w3id.org/lehrplan/ontology/> is available. "
            "You MUST include FROM clauses for the graphs you need. "
            f"Available graphs: {graph_list}"
        )

        @mcp.tool(name="sparql_query", description=description)
        async def sparql_query(
            query: Annotated[str, Field(description="The full SPARQL SELECT query to execute")],
        ) -> str:
            results = await sparql.query(query)
            return SparqlClient.format_results(results)
