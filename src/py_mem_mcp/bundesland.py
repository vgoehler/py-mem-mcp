"""Bundesland (German federal state) data and name/code/URI resolution."""

from dataclasses import dataclass

BUNDESLAND_URI: dict[str, str] = {
    "BW": "https://w3id.org/lehrplan/ontology/LP_3000049",
    "BY": "https://w3id.org/lehrplan/ontology/LP_3000051",
    "BE": "https://w3id.org/lehrplan/ontology/LP_3000048",
    "BB": "https://w3id.org/lehrplan/ontology/LP_3000057",
    "HB": "https://w3id.org/lehrplan/ontology/LP_3000056",
    "HH": "https://w3id.org/lehrplan/ontology/LP_3000045",
    "HE": "https://w3id.org/lehrplan/ontology/LP_3000050",
    "MV": "https://w3id.org/lehrplan/ontology/LP_3000052",
    "NI": "https://w3id.org/lehrplan/ontology/LP_3000043",
    "NW": "https://w3id.org/lehrplan/ontology/LP_3000044",
    "RP": "https://w3id.org/lehrplan/ontology/LP_3000046",
    "SL": "https://w3id.org/lehrplan/ontology/LP_3000055",
    "SN": "https://w3id.org/lehrplan/ontology/LP_3000047",
    "ST": "https://w3id.org/lehrplan/ontology/LP_3000053",
    "SH": "https://w3id.org/lehrplan/ontology/LP_3000054",
    "TH": "https://w3id.org/lehrplan/ontology/LP_3000031",
}

BUNDESLAND_NAME: dict[str, str] = {
    "baden-württemberg": "BW",
    "bayern": "BY",
    "berlin": "BE",
    "brandenburg": "BB",
    "bremen": "HB",
    "hamburg": "HH",
    "hessen": "HE",
    "mecklenburg-vorpommern": "MV",
    "niedersachsen": "NI",
    "nordrhein-westfalen": "NW",
    "rheinland-pfalz": "RP",
    "saarland": "SL",
    "sachsen": "SN",
    "sachsen-anhalt": "ST",
    "schleswig-holstein": "SH",
    "thüringen": "TH",
}


@dataclass
class BundeslandInfo:
    """Resolved information about a German federal state."""

    code: str
    uri: str


class BundeslandRegistry:
    """Registry for resolving German federal state codes, names, and URIs."""

    def resolve(self, input_str: str) -> BundeslandInfo:
        """Resolve a Bundesland name, two-letter code, or URI to a BundeslandInfo.

        Accepts:
            - Two-letter code (case-insensitive): "BY", "sn"
            - Full German name (case-insensitive): "Bayern", "sachsen"
            - Full URI: "https://w3id.org/lehrplan/ontology/LP_3000051"

        Raises:
            ValueError: If the input cannot be resolved.
        """
        trimmed = input_str.strip()

        # Two-letter code (case-insensitive)
        upper = trimmed.upper()
        if upper in BUNDESLAND_URI:
            return BundeslandInfo(code=upper, uri=BUNDESLAND_URI[upper])

        # Full name (case-insensitive)
        lower = trimmed.lower()
        if lower in BUNDESLAND_NAME:
            code = BUNDESLAND_NAME[lower]
            return BundeslandInfo(code=code, uri=BUNDESLAND_URI[code])

        # Already a URI — reverse-lookup the code
        if trimmed.startswith("http"):
            for code, uri in BUNDESLAND_URI.items():
                if uri == trimmed:
                    return BundeslandInfo(code=code, uri=trimmed)
            return BundeslandInfo(code="", uri=trimmed)

        raise ValueError(
            f'Unknown Bundesland: "{input_str}". '
            "Use a code (BY, SN, RP, ...) or name (Bayern, Sachsen, ...)."
        )
