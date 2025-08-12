import os
import shutil
import tempfile
import pytest
from utils import db

@pytest.fixture(scope="function")
def temp_db(monkeypatch):
    # crea cartella temporanea
    tmpdir = tempfile.mkdtemp()
    db_path = os.path.join(tmpdir, "fatture_test.db")
    monkeypatch.setattr(db, "DB_NAME", db_path)
    monkeypatch.setattr(db, "DB_PATH", db_path)
    db.init_db()
    yield db_path
    shutil.rmtree(tmpdir)
