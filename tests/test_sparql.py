"""Unit tests for py_mem_mcp.sparql."""

import pytest

from py_mem_mcp.sparql import SparqlBinding, SparqlClient, SparqlResults


class TestSparqlBinding:
    def test_basic_fields(self):
        b = SparqlBinding(type="uri", value="https://example.com")
        assert b.type == "uri"
        assert b.value == "https://example.com"
        assert b.lang is None
        assert b.datatype is None

    def test_optional_fields(self):
        b = SparqlBinding(type="literal", value="hello", lang="de", datatype=None)
        assert b.lang == "de"


class TestSparqlResults:
    def test_empty_bindings(self):
        r = SparqlResults(vars=["a", "b"])
        assert r.bindings == []

    def test_format_no_bindings(self):
        r = SparqlResults(vars=["a", "b"])
        assert SparqlClient.format_results(r) == "No results."

    def test_format_single_row(self):
        r = SparqlResults(
            vars=["uri", "label"],
            bindings=[
                {
                    "uri": SparqlBinding(type="uri", value="https://example.com"),
                    "label": SparqlBinding(type="literal", value="Test"),
                }
            ],
        )
        text = SparqlClient.format_results(r)
        assert "uri | label" in text
        assert "---" in text
        assert "https://example.com | Test" in text

    def test_format_missing_var_in_binding(self):
        r = SparqlResults(
            vars=["uri", "label"],
            bindings=[
                {
                    "uri": SparqlBinding(type="uri", value="https://example.com"),
                }
            ],
        )
        text = SparqlClient.format_results(r)
        assert "https://example.com | " in text

    def test_format_multiple_rows(self):
        r = SparqlResults(
            vars=["x"],
            bindings=[
                {"x": SparqlBinding(type="literal", value="row1")},
                {"x": SparqlBinding(type="literal", value="row2")},
            ],
        )
        text = SparqlClient.format_results(r)
        lines = text.splitlines()
        assert lines[0] == "x"
        assert lines[1] == "---"
        assert lines[2] == "row1"
        assert lines[3] == "row2"


class TestSparqlClientInit:
    def test_endpoint_stored(self):
        client = SparqlClient("https://sparql.example.com/sparql")
        assert client.endpoint == "https://sparql.example.com/sparql"
