
from ssa import db

def test_db_init_and_goal_save(tmp_path, monkeypatch):
    # Point DB to a temp file
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "mentor.db")
    db.init_db()
    gid = db.save_goal("Test Goal", None, None, None)
    assert isinstance(gid, int) and gid > 0
