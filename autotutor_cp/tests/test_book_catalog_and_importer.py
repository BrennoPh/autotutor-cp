"""Tests for canonical book catalog, open book ingestion, and user PDF/book importer."""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch, MagicMock
import pytest

from core.book_catalog import all_books, books_for_topic, format_reading_recommendations
from core.knowledge import KnowledgeBase
from scripts.import_user_books import clean_book_text, chunk_text, import_book


def test_canonical_book_catalog_structure_and_retrieval():
    catalog = all_books()
    assert len(catalog) >= 10
    book_ids = {b['id'] for b in catalog}
    assert 'clrs' in book_ids
    assert 'cp4' in book_ids
    assert 'cph' in book_ids
    assert 'erickson_alg' in book_ids

    graph_books = books_for_topic('graph')
    assert len(graph_books) >= 3
    # Check that open-access books are prioritized first
    assert graph_books[0]['open_access'] is True
    assert any('CLRS' in b['title'] or 'Algorithms' in b['title'] for b in graph_books)

    recs_md = format_reading_recommendations('graph')
    assert '📚 Leituras Recomendadas nos Livros Clássicos' in recs_md
    assert 'Capítulo recomendado' in recs_md


def test_clean_book_text_removes_running_headers_and_page_numbers():
    dirty = "Texto inicial.\n\n42\n\nPage 42 of 500\n\nContinuação do capítulo com conteúdo importante."
    cleaned = clean_book_text(dirty)
    assert '42' not in cleaned.splitlines()
    assert 'Page 42 of 500' not in cleaned
    assert 'Texto inicial.' in cleaned
    assert 'Continuação do capítulo com conteúdo importante.' in cleaned


def test_chunk_text_splits_on_headings_and_size():
    sample = (
        "# Chapter 1: Introduction to Graphs\n\n"
        + "A graph is a set of vertices and edges. " * 30
        + "\n\n# Chapter 2: Breadth-First Search\n\n"
        + "BFS explores layer by layer using a queue. " * 30
    )
    chunks = chunk_text(sample, max_chunk_chars=500)
    assert len(chunks) >= 2
    headings = [h for h, _ in chunks]
    assert any('Introduction to Graphs' in h or 'Breadth-First Search' in h for h in headings)


def test_import_user_books_dry_run_and_real_import(tmp_path):
    book_txt = tmp_path / "meu_livro_grafos.txt"
    book_txt.write_text(
        "# Capítulo 1: Grafos Fundamentais\n\n"
        "Grafos são modelagens de conexões entre estados em programação competitiva.\n\n"
        + "Explicação teórica de grafos com adjacência e matrizes. " * 20
    )

    # Dry run test
    count_dry = import_book(book_txt, dry_run=True)
    assert count_dry >= 1

    # Real import into a temporary KnowledgeBase
    kb_path = tmp_path / "temp_kb.sqlite3"
    kb = KnowledgeBase(kb_path)
    count_real = import_book(book_txt, title="Manual de Grafos", author="Professor Teste", topic="graph", dry_run=False, kb=kb)
    assert count_real >= 1

    # Verify retrieval from temporary knowledge base
    ctx, refs = kb.context("Grafos Fundamentais modelagens", external_only=True)
    assert len(refs) >= 1
    assert "Manual de Grafos" in refs[0]['title'] or "meu_livro_grafos" in refs[0]['title']


def test_tutor_generates_study_with_canonical_book_reading_recommendations():
    from core.codigen_tutor import CodigenTutor
    from core.llm_client import LLMClient

    llm = LLMClient('Gemini', 'key', 'test')
    client = MagicMock()
    client.__enter__.return_value = client
    client.models.generate_content.return_value = SimpleNamespace(
        text="# Aula de Grafos\n```mermaid\ngraph TD\n  1 --> 2\n```\nExplicação passo a passo."
    )

    with patch.object(llm, '_gemini_client', return_value=client):
        result = CodigenTutor(llm).generate_material(
            'Explicação', 'Grafos', 'Iniciante', '',
            learning_request='Quero aula de BFS',
            length='Longo', depth='Aprofundada'
        )

    assert "📚 Leituras Recomendadas nos Livros Clássicos" in result
    assert "Capítulo recomendado" in result
