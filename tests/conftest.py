"""PyTest configuration and fixtures."""

import tempfile
from pathlib import Path

import pytest

from rdflib import Graph, Namespace
from rdflib.namespace import OWL, RDF, RDFS


EX = Namespace("http://example.org/ontology#")


@pytest.fixture
def sample_ontology_content() -> str:
    """Minimal valid OWL ontology content."""
    return """<?xml version="1.0"?>
<rdf:RDF xmlns="http://example.org/ontology#"
     xml:base="http://example.org/ontology"
     xmlns:owl="http://www.w3.org/2002/07/owl#"
     xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
     xmlns:xml="http://www.w3.org/XML/1998/namespace"
     xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
     xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">
    <owl:Ontology rdf:about="http://example.org/ontology"/>
    <owl:Class rdf:about="http://example.org/ontology#Customer">
        <rdfs:label xml:lang="en">Customer</rdfs:label>
        <rdfs:comment>A customer entity</rdfs:comment>
    </owl:Class>
    <owl:Class rdf:about="http://example.org/ontology#Product">
        <rdfs:label xml:lang="en">Product</rdfs:label>
        <rdfs:comment>A product entity</rdfs:comment>
    </owl:Class>
</rdf:RDF>"""


@pytest.fixture
def sample_ontology_path(tmp_path: Path, sample_ontology_content: str) -> Path:
    """Create a temporary sample ontology file."""
    path = tmp_path / "sample.owl"
    path.write_text(sample_ontology_content)
    return path


@pytest.fixture
def sample_ontology_v2_content() -> str:
    """Sample ontology with additional entity (for diff testing)."""
    return """<?xml version="1.0"?>
<rdf:RDF xmlns="http://example.org/ontology#"
     xml:base="http://example.org/ontology"
     xmlns:owl="http://www.w3.org/2002/07/owl#"
     xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
     xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">
    <owl:Ontology rdf:about="http://example.org/ontology"/>
    <owl:Class rdf:about="http://example.org/ontology#Customer">
        <rdfs:label>Customer</rdfs:label>
        <rdfs:comment>A customer entity</rdfs:comment>
    </owl:Class>
    <owl:Class rdf:about="http://example.org/ontology#Product">
        <rdfs:label>Product</rdfs:label>
        <rdfs:comment>A product entity</rdfs:comment>
    </owl:Class>
    <owl:Class rdf:about="http://example.org/ontology#Subscription">
        <rdfs:label>Subscription</rdfs:label>
        <rdfs:comment>A subscription entity</rdfs:comment>
    </owl:Class>
</rdf:RDF>"""


@pytest.fixture
def sample_ontology_v2_path(tmp_path: Path, sample_ontology_v2_content: str) -> Path:
    """Create sample ontology v2 file."""
    path = tmp_path / "sample_v2.owl"
    path.write_text(sample_ontology_v2_content)
    return path


@pytest.fixture
def temp_storage(tmp_path: Path) -> Path:
    """Temporary storage path for version control."""
    return tmp_path / "versions"


@pytest.fixture
def test_database_path(tmp_path: Path) -> Path:
    """Create a minimal SQLite test database."""
    import sqlite3
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE customer (id INTEGER, name TEXT)")
    conn.execute("CREATE TABLE product (id INTEGER, name TEXT)")
    conn.commit()
    conn.close()
    return db_path
