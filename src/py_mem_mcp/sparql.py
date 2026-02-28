"""SPARQL client for querying the MEM ontology triple store."""

from dataclasses import dataclass, field

import httpx


@dataclass
class SparqlBinding:
    """A single binding value returned by a SPARQL query."""

    type: str
    value: str
    lang: str | None = None
    datatype: str | None = None


@dataclass
class SparqlResults:
    """Structured results from a SPARQL SELECT query."""

    vars: list[str]
    bindings: list[dict[str, SparqlBinding]] = field(default_factory=list)


class SparqlClient:
    """Async client for executing SPARQL queries against a triple store endpoint."""

    def __init__(self, endpoint: str) -> None:
        self.endpoint = endpoint

    async def query(self, sparql: str) -> SparqlResults:
        """Execute a SPARQL SELECT query and return structured results.

        Args:
            sparql: The full SPARQL SELECT query string.

        Raises:
            RuntimeError: If the HTTP request fails or returns a non-success status.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.endpoint,
                content=sparql.encode(),
                headers={
                    "Content-Type": "application/sparql-query",
                    "Accept": "application/sparql-results+json",
                },
                timeout=30.0,
            )

        if not response.is_success:
            body = response.text[:200]
            raise RuntimeError(
                f"SPARQL query failed ({response.status_code}): {body}"
            )

        data = response.json()
        vars_ = data["head"]["vars"]
        bindings: list[dict[str, SparqlBinding]] = []
        for raw in data["results"]["bindings"]:
            binding: dict[str, SparqlBinding] = {}
            for var, val in raw.items():
                binding[var] = SparqlBinding(
                    type=val["type"],
                    value=val["value"],
                    lang=val.get("xml:lang"),
                    datatype=val.get("datatype"),
                )
            bindings.append(binding)

        return SparqlResults(vars=vars_, bindings=bindings)

    @staticmethod
    def format_results(results: SparqlResults) -> str:
        """Format SPARQL results as a human-readable text table.

        Args:
            results: The SparqlResults to format.

        Returns:
            A string with a header row, a separator, and one data row per binding.
            Returns "No results." if there are no bindings.
        """
        if not results.bindings:
            return "No results."

        rows = [
            " | ".join(
                binding[v].value if v in binding else "" for v in results.vars
            )
            for binding in results.bindings
        ]
        header = " | ".join(results.vars)
        return "\n".join([header, "---", *rows])
