"""Make the application importable for direct pytest invocations."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest


@pytest.fixture(autouse=True)
def isolated_learning_database(tmp_path, monkeypatch):
    monkeypatch.setenv('AUTOTUTOR_PROGRESS_DB', str(tmp_path / 'learning.sqlite3'))

    monkeypatch.setenv('AUTOTUTOR_KNOWLEDGE_DB', str(tmp_path / 'knowledge.sqlite3'))
