"""Named graph registry for managing SPARQL graph URIs from environment variables."""

import os

from .config import require_env


class GraphRegistry:
    """Registry for managing named SPARQL graphs used in MEM ontology queries.

    Infrastructure graphs (ontology, Schulart, Schulfach) are always required.
    State graphs (one per Bundesland) are discovered dynamically from environment
    variables with the prefix ``GRAPH_STATE_<CODE>``.
    """

    def __init__(self) -> None:
        self.infra_graphs: list[str] = [
            require_env("GRAPH_ONTOLOGY"),
            require_env("GRAPH_SCHULART"),
            require_env("GRAPH_SCHULFACH"),
        ]
        self.state_graphs: dict[str, str] = {}
        for key, value in os.environ.items():
            if key.startswith("GRAPH_STATE_") and value:
                code = key[len("GRAPH_STATE_"):]
                self.state_graphs[code] = value

    @property
    def all_graphs(self) -> list[str]:
        """All known graphs: infrastructure graphs plus all state graphs."""
        return self.infra_graphs + list(self.state_graphs.values())

    def graphs_for_bundesland(self, code: str) -> list[str]:
        """Return the graphs relevant for a given Bundesland code.

        Always includes the infrastructure graphs; adds the state-specific
        graph when one is registered for *code*.
        """
        state_graph = self.state_graphs.get(code)
        if state_graph:
            return self.infra_graphs + [state_graph]
        return list(self.infra_graphs)

    @staticmethod
    def from_clauses(graphs: list[str]) -> str:
        """Build SPARQL ``FROM`` clauses for the given list of graph URIs."""
        return "\n".join(f"FROM <{g}>" for g in graphs)
