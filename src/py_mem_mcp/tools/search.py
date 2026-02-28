"""Full-text search tool for the MEM ontology MCP server."""

from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from ..bundesland import BundeslandRegistry
from ..graphs import GraphRegistry
from ..sparql import SparqlClient
from .lehrplan import _resolve_schulfach_uri

_RESULTS_LIMIT = 50


class SearchTools:
    """Provides the ``search`` tool for full-text search across Lehrplan nodes."""

    def __init__(
        self,
        sparql_client: SparqlClient,
        graph_registry: GraphRegistry,
        bundesland_registry: BundeslandRegistry,
    ) -> None:
        self.sparql = sparql_client
        self.graphs = graph_registry
        self.bl_registry = bundesland_registry

    def register(self, mcp: FastMCP) -> None:
        """Register all search tools with the given FastMCP server instance."""
        sparql = self.sparql
        graphs = self.graphs
        bl_registry = self.bl_registry

        @mcp.tool(
            name="search",
            description=(
                "Full-text search across all Lehrplan nodes by keyword. "
                "Uses prefix matching (e.g. 'Fisch' also finds 'Fische'). "
                "Returns matching nodes with their parent Lehrplan for context. "
                "Optionally filter by Bundesland and/or Schulfach."
            ),
        )
        async def search(
            query: Annotated[
                str,
                Field(description="Search term (e.g. 'Fisch', 'Evolution')"),
            ],
            bundesland: Annotated[
                str | None,
                Field(
                    description=(
                        "Optional: state code (BY, SN, RP, ...) or name "
                        "(Bayern, Sachsen, ...) to limit search"
                    )
                ),
            ] = None,
            schulfach: Annotated[
                str | None,
                Field(
                    description=(
                        "Optional: subject name in German (e.g. Biologie, Mathematik) "
                        "to limit search to a specific subject"
                    )
                ),
            ] = None,
        ) -> str:
            search_graphs = graphs.all_graphs
            bl_uri: str | None = None

            if bundesland:
                bl = bl_registry.resolve(bundesland)
                search_graphs = graphs.graphs_for_bundesland(bl.code)
                bl_uri = bl.uri

            contains_expr = " AND ".join(
                f"'{w.replace(chr(39), '')}*'"
                for w in query.strip().split()
            )

            if schulfach:
                if not bl_uri:
                    raise ValueError(
                        "Bundesland is required when filtering by Schulfach."
                    )
                sf_uri = await _resolve_schulfach_uri(
                    schulfach, bl_uri, search_graphs, sparql
                )
                sparql_query = f"""
PREFIX lp: <https://w3id.org/lehrplan/ontology/>
SELECT DISTINCT ?s ?label ?lp ?lpLabel
{GraphRegistry.from_clauses(search_graphs)}
WHERE {{
  ?s rdfs:label ?label .
  ?label bif:contains "{contains_expr}" .
  ?lp lp:LP_0000008+ ?s .
  ?lp lp:LP_0000537 <{sf_uri}> .
  ?lp rdfs:label ?lpLabel .
}}
ORDER BY ?s
LIMIT {_RESULTS_LIMIT}"""
            else:
                sparql_query = f"""
PREFIX lp: <https://w3id.org/lehrplan/ontology/>
SELECT DISTINCT ?s ?label ?parent ?parentLabel
{GraphRegistry.from_clauses(search_graphs)}
WHERE {{
  ?s rdfs:label ?label .
  ?label bif:contains "{contains_expr}" .
  OPTIONAL {{
    ?parent lp:LP_0000008 ?s .
    ?parent rdfs:label ?parentLabel .
  }}
}}
ORDER BY ?s
LIMIT {_RESULTS_LIMIT}"""

            results = await sparql.query(sparql_query)
            if not results.bindings:
                return f'No results found for "{query}".'

            text = SparqlClient.format_results(results)
            if len(results.bindings) == _RESULTS_LIMIT:
                text += (
                    "\n\n(Results limited to 50. "
                    "Try a more specific query or add filters.)"
                )
            return text
