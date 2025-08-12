import zipfile
from io import BytesIO
from utils import backup

def test_backup_creates_zip(temp_db):
    buf, filename = backup.build_backup_zip_for_user("test@example.com")

    # Controllo tipo e nome file
    assert isinstance(buf, BytesIO)
    assert filename.startswith("FAi_backup_")
    assert filename.endswith(".zip")

    # Verifica che il buffer contenga un file ZIP valido
    buf.seek(0)
    assert zipfile.is_zipfile(buf)

    # Apri e controlla che abbia almeno un file dentro
    with zipfile.ZipFile(buf, "r") as z:
        namelist = z.namelist()
        assert len(namelist) > 0
