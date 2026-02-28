# py-mem-mcp

A Python implementation of the MEM (Metadata for Education Media) ontology MCP server,
built with [FastMCP](https://github.com/jlowin/fastmcp) and managed with
[Poetry](https://python-poetry.org/).

## Features

The server exposes the following MCP tools:

| Tool | Description |
|------|-------------|
| `sparql_query` | Execute arbitrary SPARQL SELECT queries against the MEM triple store |
| `list_bundeslaender` | List all German federal states available in the ontology |
| `list_schulfaecher` | List all school subjects for a given state |
| `list_schularten` | List all school types for a given state |
| `find_lehrplaene` | Find curricula filtered by state, subject, school type, or grade |
| `get_lehrplan_tree` | Get the hierarchical structure of a Lehrplan (depth-limited) |
| `get_children` | Get direct children of a specific node |
| `search` | Full-text search across Lehrplan nodes by keyword |

## Project structure

```
py-mem-mcp/
├── pyproject.toml          # Poetry project definition
├── Dockerfile              # Multi-stage Docker image
├── docker-compose.yml
├── .env.example            # Required environment variables
├── src/
│   └── py_mem_mcp/
│       ├── config.py       # Environment variable helpers
│       ├── sparql.py       # SparqlClient class
│       ├── bundesland.py   # BundeslandRegistry class
│       ├── graphs.py       # GraphRegistry class
│       ├── server.py       # FastMCP server entry point
│       └── tools/
│           ├── query.py    # sparql_query tool
│           ├── listing.py  # list_* tools
│           ├── lehrplan.py # find/get Lehrplan tools
│           └── search.py   # search tool
└── tests/                  # pytest unit tests
```

## Installation

```bash
# Install dependencies
poetry install

# Copy and edit the environment file
cp .env.example .env
```

## Configuration

All configuration is via environment variables (loaded from `.env`).

| Variable | Description | Required |
|----------|-------------|----------|
| `SPARQL_ENDPOINT` | SPARQL endpoint URL | ✔ |
| `GRAPH_ONTOLOGY` | Ontology graph URI | ✔ |
| `GRAPH_SCHULART` | Schulart graph URI | ✔ |
| `GRAPH_SCHULFACH` | Schulfach graph URI | ✔ |
| `GRAPH_STATE_<CODE>` | Graph URI for a state (e.g. `GRAPH_STATE_SN`) | optional |
| `PORT` | HTTP port (default: `8000`) | optional |

## Running the server

```bash
# Development
poetry run py-mem-mcp

# Or directly
poetry run python -m py_mem_mcp.server
```

## Running with Docker

```bash
cp .env.example .env   # edit as needed
docker compose up -d
```

The server will be available at `http://localhost:8000/mcp`.

### MCP client configuration

```json
{
  "mcpServers": {
    "mem-ontology": {
      "type": "http",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

## Running tests

```bash
poetry run pytest
```

## State codes

| Code | State |
|------|-------|
| BW | Baden-Württemberg |
| BY | Bayern |
| BE | Berlin |
| BB | Brandenburg |
| HB | Bremen |
| HH | Hamburg |
| HE | Hessen |
| MV | Mecklenburg-Vorpommern |
| NI | Niedersachsen |
| NW | Nordrhein-Westfalen |
| RP | Rheinland-Pfalz |
| SL | Saarland |
| SN | Sachsen |
| ST | Sachsen-Anhalt |
| SH | Schleswig-Holstein |
| TH | Thüringen |

> Currently, curriculum data is available for **BY**, **SN**, and **RP**.

## License

CC0-1.0
