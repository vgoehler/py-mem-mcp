"""Listing tools: list_bundeslaender, list_schulfaecher, list_schularten."""

from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from ..bundesland import BundeslandRegistry
from ..graphs import GraphRegistry
from ..sparql import SparqlClient


class ListingTools:
    """Provides tools that list available Bundesländer, Schulfächer, and Schularten."""

    def __init__(
        self,
        sparql_client: SparqlClient,
        graph_registry: GraphRegistry,
        bundesland_registry: BundeslandRegistry,
    ) -> None:
        self.sparql = sparql_client
        self.graphs = graph_registry
        self.bundesland = bundesland_registry

    def register(self, mcp: FastMCP) -> None:
        """Register all listing tools with the given FastMCP server instance."""
        sparql = self.sparql
        graphs = self.graphs
        bl_registry = self.bundesland

        @mcp.tool(
            name="list_bundeslaender",
            description=(
                "List all German federal states (Bundesländer) available in the "
                "ontology with their codes and URIs."
            ),
        )
        async def list_bundeslaender() -> str:
            query = f"""
PREFIX lp: <https://w3id.org/lehrplan/ontology/>
SELECT DISTINCT ?uri ?label
{GraphRegistry.from_clauses(graphs.all_graphs)}
WHERE {{
  ?s lp:LP_0000029 ?uri .
  ?uri rdfs:label ?label .
  FILTER(lang(?label) = "de")
}}
ORDER BY ?label"""
            results = await sparql.query(query)
            return SparqlClient.format_results(results)

        @mcp.tool(
            name="list_schulfaecher",
            description=(
                "List all school subjects (Schulfächer) for a Bundesland. "
                "Accepts a state code (BY, SN, RP, ...) or name (Bayern, Sachsen, ...)."
            ),
        )
        async def list_schulfaecher(
            bundesland: Annotated[
                str,
                Field(
                    description=(
                        "State code (BY, SN, RP, ...) or name "
                        "(Bayern, Sachsen, Rheinland-Pfalz, ...)"
                    ),
                ),
            ],
        ) -> str:
            bl = bl_registry.resolve(bundesland)
            bl_graphs = graphs.graphs_for_bundesland(bl.code)
            query = f"""
PREFIX lp: <https://w3id.org/lehrplan/ontology/>
SELECT DISTINCT ?uri (SAMPLE(?l) AS ?label)
{GraphRegistry.from_clauses(bl_graphs)}
WHERE {{
  ?s lp:LP_0000537 ?uri .
  ?uri rdfs:label ?l .
  ?s lp:LP_0000029 <{bl.uri}> .
  FILTER(lang(?l) = "de")
}}
GROUP BY ?uri
ORDER BY ?label"""
            results = await sparql.query(query)
            return SparqlClient.format_results(results)

        @mcp.tool(
            name="list_schularten",
            description=(
                "List all school types (Schularten) for a Bundesland. "
                "Accepts a state code (BY, SN, RP, ...) or name (Bayern, Sachsen, ...)."
            ),
        )
        async def list_schularten(
            bundesland: Annotated[
                str,
                Field(
                    description=(
                        "State code (BY, SN, RP, ...) or name "
                        "(Bayern, Sachsen, Rheinland-Pfalz, ...)"
                    ),
                ),
            ],
        ) -> str:
            bl = bl_registry.resolve(bundesland)
            bl_graphs = graphs.graphs_for_bundesland(bl.code)
            query = f"""
PREFIX lp: <https://w3id.org/lehrplan/ontology/>
SELECT DISTINCT ?uri (SAMPLE(?l) AS ?label)
{GraphRegistry.from_clauses(bl_graphs)}
WHERE {{
  ?s lp:LP_0000812 ?uri .
  ?uri rdfs:label ?l .
  ?s lp:LP_0000029 <{bl.uri}> .
}}
GROUP BY ?uri
ORDER BY ?label"""
            results = await sparql.query(query)
            return SparqlClient.format_results(results)
