"""MEM ontology MCP server entry point.

Assembles all components and starts the FastMCP server using the
streamable-HTTP transport on the configured port.
"""

import os
import sys

from fastmcp import FastMCP

from .bundesland import BundeslandRegistry
from .graphs import GraphRegistry
from .sparql import SparqlClient
from .tools.lehrplan import LehrplanTools
from .tools.listing import ListingTools
from .tools.query import QueryTools
from .tools.search import SearchTools


def create_server() -> FastMCP:
    """Assemble and return a fully configured FastMCP server.

    Initialises the graph registry, SPARQL client, and Bundesland registry,
    then registers all MCP tools.
    """
    graph_registry = GraphRegistry()
    sparql_endpoint = os.environ.get("SPARQL_ENDPOINT", "")
    if not sparql_endpoint:
        from .config import require_env
        sparql_endpoint = require_env("SPARQL_ENDPOINT")

    sparql_client = SparqlClient(sparql_endpoint)
    bundesland_registry = BundeslandRegistry()

    mcp = FastMCP("mem-ontology-server")

    QueryTools(sparql_client, graph_registry).register(mcp)
    ListingTools(sparql_client, graph_registry, bundesland_registry).register(mcp)
    LehrplanTools(sparql_client, graph_registry, bundesland_registry).register(mcp)
    SearchTools(sparql_client, graph_registry, bundesland_registry).register(mcp)

    return mcp


def check_port():
    port_str = os.environ.get("PORT", "3000")
    try:
        port = int(port_str)
        if not 1 <= port <= 65535:
            raise ValueError
    except ValueError:
        print(
            f'Invalid PORT value: "{port_str}". Must be a number between 1 and 65535.',
            file=sys.stderr,
        )
        sys.exit(1)
    return port


def main() -> None:
    """Entry point for the MEM ontology MCP server."""
    port = check_port()

    mcp = create_server()

    sparql_endpoint = os.environ.get("SPARQL_ENDPOINT", "(not set)")
    print(f"MEM Ontology MCP Server starting on port {port}", file=sys.stderr)
    print(f"SPARQL endpoint: {sparql_endpoint}", file=sys.stderr)

    mcp.run(transport="streamable-http", host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
