import pytest


@pytest.fixture(autouse=True)
def _isolated_cwd(tmp_path, monkeypatch):
    """shortest_path() and main() write exploration.csv / statistics.txt to
    the current directory; keep those out of the repo during tests."""
    monkeypatch.chdir(tmp_path)
