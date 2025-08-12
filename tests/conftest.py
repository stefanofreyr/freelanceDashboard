import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import os
import shutil
import tempfile
import pytest
import gc
from utils import db

@pytest.fixture(scope="function")
def temp_db(monkeypatch):
    tmpdir = tempfile.mkdtemp()
    db_path = os.path.join(tmpdir, "fatture_test.db")
    monkeypatch.setattr(db, "DB_NAME", db_path)
    monkeypatch.setattr(db, "DB_PATH", db_path)
    db.init_db()
    yield db_path
    # Forza chiusura connessioni DB prima di cancellare
    gc.collect()
    try:
        shutil.rmtree(tmpdir)
    except PermissionError:
        pass