"""Lehrplan tools: find_lehrplaene, get_lehrplan_tree, get_children.

These tools navigate the hierarchical curriculum (Lehrplan) data stored
in the MEM ontology triple store.
"""

from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from ..bundesland import BundeslandRegistry
from ..graphs import GraphRegistry
from ..sparql import SparqlClient


async def _resolve_schulfach_uri(
    name: str,
    bundesland_uri: str,
    bl_graphs: list[str],
    sparql: SparqlClient,
) -> str:
    """Resolve a Schulfach name to its URI for the given Bundesland."""
    query = f"""
PREFIX lp: <https://w3id.org/lehrplan/ontology/>
SELECT ?uri
{GraphRegistry.from_clauses(bl_graphs)}
WHERE {{
  ?s lp:LP_0000537 ?uri .
  ?uri rdfs:label ?l .
  ?s lp:LP_0000029 <{bundesland_uri}> .
  FILTER(LCASE(STR(?l)) = "{name.lower()}")
}}
LIMIT 1"""
    results = await sparql.query(query)
    if not results.bindings:
        raise ValueError(
            f'Schulfach "{name}" not found for this Bundesland. '
            "Use list_schulfaecher to see available subjects."
        )
    return results.bindings[0]["uri"].value


async def _resolve_schulart_uri(
    name: str,
    bundesland_uri: str,
    bl_graphs: list[str],
    sparql: SparqlClient,
) -> str:
    """Resolve a Schulart name to its URI for the given Bundesland."""
    query = f"""
PREFIX lp: <https://w3id.org/lehrplan/ontology/>
SELECT ?uri
{GraphRegistry.from_clauses(bl_graphs)}
WHERE {{
  ?s lp:LP_0000812 ?uri .
  ?uri rdfs:label ?l .
  ?s lp:LP_0000029 <{bundesland_uri}> .
  FILTER(LCASE(STR(?l)) = "{name.lower()}")
}}
LIMIT 1"""
    results = await sparql.query(query)
    if not results.bindings:
        raise ValueError(
            f'Schulart "{name}" not found for this Bundesland. '
            "Use list_schularten to see available school types."
        )
    return results.bindings[0]["uri"].value


class LehrplanTools:
    """Provides tools for navigating Lehrplan hierarchy data."""

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
        """Register all Lehrplan tools with the given FastMCP server instance."""
        sparql = self.sparql
        graphs = self.graphs
        bl_registry = self.bl_registry

        @mcp.tool(
            name="find_lehrplaene",
            description=(
                "Find curricula (Lehrpläne) by Bundesland, optionally filtered by "
                "Schulfach, Schulart, or Jahrgangsstufe. "
                "Use state codes/names. For Schulfach and Schulart, use the German "
                "name as shown by the list tools."
            ),
        )
        async def find_lehrplaene(
            bundesland: Annotated[
                str,
                Field(
                    description="State code (BY, SN, RP, ...) or name (Bayern, Sachsen, ...)"
                ),
            ],
            schulfach: Annotated[
                str | None,
                Field(description="Optional: subject name in German (e.g. Biologie, Mathematik)"),
            ] = None,
            schulart: Annotated[
                str | None,
                Field(description="Optional: school type name (e.g. Gymnasium, Grundschule)"),
            ] = None,
            jahrgangsstufe: Annotated[
                int | None,
                Field(description="Optional: grade level (1–13)", ge=1, le=13),
            ] = None,
        ) -> str:
            bl = bl_registry.resolve(bundesland)
            bl_graphs = graphs.graphs_for_bundesland(bl.code)
            filters = [f"?s lp:LP_0000029 <{bl.uri}> ."]

            if schulfach:
                sf_uri = await _resolve_schulfach_uri(schulfach, bl.uri, bl_graphs, sparql)
                filters.append(f"?s lp:LP_0000537 <{sf_uri}> .")
            if schulart:
                sa_uri = await _resolve_schulart_uri(schulart, bl.uri, bl_graphs, sparql)
                filters.append(f"?s lp:LP_0000812 <{sa_uri}> .")
            if jahrgangsstufe is not None:
                js_uri = (
                    f"https://w3id.org/lehrplan/ontology/"
                    f"LP_{2000000 + jahrgangsstufe:07d}"
                )
                filters.append(f"?s lp:LP_0000026 <{js_uri}> .")

            filter_block = "\n  ".join(filters)
            query = f"""
PREFIX lp: <https://w3id.org/lehrplan/ontology/>
SELECT DISTINCT ?s ?label
{GraphRegistry.from_clauses(bl_graphs)}
WHERE {{
  ?lpsubclass rdfs:subClassOf* lp:LP_0000438 .
  ?s rdf:type ?lpsubclass .
  ?s rdfs:label ?label .
  {filter_block}
}}
ORDER BY ?label
LIMIT 50"""
            results = await sparql.query(query)
            return SparqlClient.format_results(results)

        @mcp.tool(
            name="get_lehrplan_tree",
            description=(
                "Get the hierarchical structure (parent-child via 'hat Teil') of a "
                "specific Lehrplan. Use a Lehrplan URI obtained from find_lehrplaene. "
                "The depth parameter controls how many levels deep the tree goes "
                "(default 2, max 10). Use get_children to drill deeper into specific nodes."
            ),
        )
        async def get_lehrplan_tree(
            lehrplan_uri: Annotated[
                str,
                Field(description="URI of the Lehrplan (from find_lehrplaene results)"),
            ],
            depth: Annotated[
                int,
                Field(description="How many levels deep to retrieve (default 2)", ge=1, le=10),
            ] = 2,
        ) -> str:
            unions: list[str] = []
            for d in range(1, depth + 1):
                if d == 1:
                    unions.append(
                        f"{{ BIND(<{lehrplan_uri}> AS ?parent) . "
                        "?parent lp:LP_0000008 ?child . }}"
                    )
                else:
                    steps = [f"<{lehrplan_uri}> lp:LP_0000008 ?step1 ."]
                    for i in range(2, d):
                        steps.append(f"?step{i - 1} lp:LP_0000008 ?step{i} .")
                    steps.append(f"BIND(?step{d - 1} AS ?parent)")
                    steps.append("?parent lp:LP_0000008 ?child .")
                    unions.append("{ " + " ".join(steps) + " }")

            union_block = "\n  UNION\n  ".join(unions)
            query = f"""
PREFIX lp: <https://w3id.org/lehrplan/ontology/>
SELECT DISTINCT ?parent ?parentLabel ?child ?childLabel
{GraphRegistry.from_clauses(graphs.all_graphs)}
WHERE {{
  {union_block}
  OPTIONAL {{ ?parent rdfs:label ?parentLabel . }}
  OPTIONAL {{ ?child rdfs:label ?childLabel . }}
}}
ORDER BY ?parent ?child"""
            results = await sparql.query(query)

            parent_uris = {b["parent"].value for b in results.bindings}
            child_uris = {b["child"].value for b in results.bindings}
            leaves = child_uris - parent_uris

            text = SparqlClient.format_results(results)
            if leaves:
                text += (
                    f"\n\n(Tree shown to depth {depth}. "
                    "Deeper levels may exist. Use get_children to explore further.)"
                )
            return text

        @mcp.tool(
            name="get_children",
            description=(
                "Get the direct children of a specific node in the Lehrplan hierarchy "
                "(via 'hat Teil'). Use this to drill down into a specific branch after "
                "using get_lehrplan_tree."
            ),
        )
        async def get_children(
            node_uri: Annotated[
                str,
                Field(description="URI of the node to get children for"),
            ],
        ) -> str:
            query = f"""
PREFIX lp: <https://w3id.org/lehrplan/ontology/>
SELECT DISTINCT ?child ?childLabel
{GraphRegistry.from_clauses(graphs.all_graphs)}
WHERE {{
  <{node_uri}> lp:LP_0000008 ?child .
  OPTIONAL {{ ?child rdfs:label ?childLabel . }}
}}
ORDER BY ?child"""
            results = await sparql.query(query)
            if not results.bindings:
                return "No children found (leaf node)."
            return SparqlClient.format_results(results)
