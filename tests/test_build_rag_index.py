"""Check index creation through retrieval using real SQLite and fixed vectors. No API calls."""

import json
import sqlite3
from unittest.mock import Mock

import pytest

from app import retrieval
from scripts.build_rag_index import build_index


@pytest.fixture
def materials(tmp_path):
    source = tmp_path / "lectures.json"
    source.write_text(json.dumps([
        {"id": f"lec{n:02d}-main", "title": f"Lecture {n}", "content": [
            {"section": "Section", "content": [
                {"id": f"lec{n:02d}-main-p001", "title": f"Page {n}",
                 "page": 1, "content": f"Text {n}"}]}]}
        for n in (1, 2, 5)
    ], ensure_ascii=False), encoding="utf-8")
    return source, tmp_path / "index.sqlite3"


def test_built_index_can_be_searched(materials, monkeypatch):
    source, database = materials
    texts = []

    def embed(text, task):
        assert task == "RETRIEVAL_DOCUMENT"
        texts.append(text)
        return [1, 0] if "Text 1" in text else [0, 1]

    result = build_index(source, database, embedder=embed)
    assert result["pages"] == 2  # Lecture 05 materials are excluded from the search scope
    assert all("Section" in text and "Page" in text for text in texts)
    monkeypatch.setattr(retrieval, "RAG_DB", database)
    monkeypatch.setattr(retrieval, "embed_text", lambda *_: [1, 0])
    hits = retrieval.search("Question")
    assert [h["page_id"] for h in hits] == ["lec01-main-p001", "lec02-main-p001"]
    assert hits[0]["content"] == "Text 1"
    assert hits[0]["distance"] == pytest.approx(0)


def test_search_returns_adjacent_pages_from_the_same_document(tmp_path, monkeypatch):
    source = tmp_path / "lectures.json"
    source.write_text(json.dumps([{
        "id": "lec01-main", "title": "Lecture 1", "content": [{
            "section": "Section", "content": [
                {"id": "z-before", "title": "Previous", "page": 10, "content": "Before"},
                {"id": "a-primary", "title": "Primary", "page": 20, "content": "Main"},
                {"id": "b-after", "title": "Next", "page": 40, "content": "After"},
            ],
        }],
    }]), encoding="utf-8")
    database = tmp_path / "index.sqlite3"
    build_index(
        source, database,
        embedder=lambda page, _: [1, 0] if "Main" in page else [0, 1],
    )
    monkeypatch.setattr(retrieval, "RAG_DB", database)
    monkeypatch.setattr(retrieval, "RAG_TOP_K", 1)
    monkeypatch.setattr(retrieval, "embed_text", lambda *_: [1, 0])

    hits = retrieval.search("Question")

    assert [hit["page_id"] for hit in hits] == ["a-primary"]
    assert [page["page_id"] for page in hits[0]["adjacent_pages"]] == ["z-before", "b-after"]


def test_adjacent_pages_use_document_and_page_order_without_duplicates():
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.execute("""CREATE TABLE chunks (
        page_id TEXT, document_id TEXT, title TEXT, page INTEGER, content TEXT, citation TEXT
    )""")
    db.executemany("INSERT INTO chunks VALUES (?, ?, ?, ?, ?, ?)", [
        ("z-page-id", "doc-a", "Previous", 10, "Before", "PDF p.10"),
        ("primary", "doc-a", "Primary", 20, "Main", "PDF p.20"),
        ("a-page-id", "doc-a", "Next", 40, "After", "PDF p.40"),
        ("other-doc", "doc-b", "Other document", 21, "Do not include", "PDF p.21"),
    ])
    hit = {"page_id": "primary", "document_id": "doc-a", "page": 20}

    adjacent = retrieval.adjacent_pages(db, hit, has_citation=True)

    assert [page["page_id"] for page in adjacent] == ["z-page-id", "a-page-id"]
    assert [page["position"] for page in adjacent] == ["previous", "next"]
    assert [page["page_label"] for page in adjacent] == ["PDF p.10", "PDF p.40"]
    assert [page["content"] for page in adjacent] == ["Before", "After"]
    assert all(page["page_id"] != hit["page_id"] for page in adjacent)
    db.close()


def test_adjacent_search_results_are_not_duplicated():
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.execute("""CREATE TABLE chunks (
        page_id TEXT, document_id TEXT, title TEXT, page INTEGER, content TEXT
    )""")
    db.executemany("INSERT INTO chunks VALUES (?, ?, ?, ?, ?)", [
        ("previous", "doc-a", "Previous", 10, "Before"),
        ("primary", "doc-a", "Primary", 20, "Main"),
        ("next", "doc-a", "Next", 40, "After"),
    ])
    results = [
        {"page_id": "primary", "document_id": "doc-a", "page": 20},
        {"page_id": "previous", "document_id": "doc-a", "page": 10},
    ]

    retrieval._attach_adjacent_pages(db, results, has_citation=False)

    assert [page["page_id"] for page in results[0]["adjacent_pages"]] == ["next"]
    assert results[1]["adjacent_pages"] == []
    db.close()


def test_existing_index_survives_failed_rebuild(materials):
    source, database = materials
    build_index(source, database, embedder=lambda *_: [1, 0])
    before = database.read_bytes()
    embed = Mock(side_effect=RuntimeError("Embedding failed"))
    with pytest.raises(FileExistsError):
        build_index(source, database, embedder=embed)
    embed.assert_not_called()
    with pytest.raises(RuntimeError, match="Embedding failed"):
        build_index(source, database, rebuild=True, embedder=embed)
    assert database.read_bytes() == before
    assert not list(database.parent.glob(".rag-build-*"))
