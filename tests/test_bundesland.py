"""Unit tests for py_mem_mcp.bundesland."""

import pytest

from py_mem_mcp.bundesland import BundeslandInfo, BundeslandRegistry


@pytest.fixture
def registry() -> BundeslandRegistry:
    return BundeslandRegistry()


class TestBundeslandRegistry:
    def test_resolve_by_code_uppercase(self, registry):
        info = registry.resolve("BY")
        assert info.code == "BY"
        assert info.uri == "https://w3id.org/lehrplan/ontology/LP_3000051"

    def test_resolve_by_code_lowercase(self, registry):
        info = registry.resolve("sn")
        assert info.code == "SN"
        assert info.uri == "https://w3id.org/lehrplan/ontology/LP_3000047"

    def test_resolve_by_full_name(self, registry):
        info = registry.resolve("Bayern")
        assert info.code == "BY"

    def test_resolve_by_full_name_case_insensitive(self, registry):
        info = registry.resolve("sachsen")
        assert info.code == "SN"

    def test_resolve_by_uri(self, registry):
        uri = "https://w3id.org/lehrplan/ontology/LP_3000046"
        info = registry.resolve(uri)
        assert info.code == "RP"
        assert info.uri == uri

    def test_resolve_unknown_uri_returns_empty_code(self, registry):
        uri = "https://example.com/unknown"
        info = registry.resolve(uri)
        assert info.code == ""
        assert info.uri == uri

    def test_resolve_unknown_string_raises(self, registry):
        with pytest.raises(ValueError, match="Unknown Bundesland"):
            registry.resolve("XY")

    def test_resolve_whitespace_stripped(self, registry):
        info = registry.resolve("  BY  ")
        assert info.code == "BY"

    def test_all_codes_present(self, registry):
        codes = ["BW", "BY", "BE", "BB", "HB", "HH", "HE", "MV",
                 "NI", "NW", "RP", "SL", "SN", "ST", "SH", "TH"]
        for code in codes:
            info = registry.resolve(code)
            assert info.code == code
            assert info.uri.startswith("https://")

    def test_bundesland_info_dataclass(self):
        info = BundeslandInfo(code="BY", uri="https://example.com")
        assert info.code == "BY"
        assert info.uri == "https://example.com"
