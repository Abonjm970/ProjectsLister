import os
import json
import tempfile
from pathlib import Path
import pytest
from projectslister.models import Project, ProjectManager


@pytest.fixture
def temp_config_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def test_project_serialization():
    p = Project(name="Test Proj", path="/tmp/test", last_opened="2026-07-28T21:14:00")
    d = p.to_dict()
    assert d == {"name": "Test Proj", "path": "/tmp/test", "last_opened": "2026-07-28T21:14:00"}
    
    p2 = Project.from_dict(d)
    assert p2.name == p.name
    assert p2.path == p.path
    assert p2.last_opened == p.last_opened


def test_empty_manager(temp_config_dir):
    pm = ProjectManager(config_dir=temp_config_dir)
    assert pm.load_projects() == []


def test_add_and_load_project(temp_config_dir):
    pm = ProjectManager(config_dir=temp_config_dir)
    test_dir = temp_config_dir / "sample_proj"
    test_dir.mkdir()

    success, err, proj = pm.add_project("Sample Project", str(test_dir))
    assert success is True
    assert err == ""
    assert proj is not None
    assert proj.name == "Sample Project"
    assert proj.path == str(test_dir.resolve())
    assert proj.last_opened is None

    loaded = pm.load_projects()
    assert len(loaded) == 1
    assert loaded[0].name == "Sample Project"


def test_validation_rules(temp_config_dir):
    pm = ProjectManager(config_dir=temp_config_dir)
    
    # Empty name
    ok, err, _ = pm.add_project("", "/tmp")
    assert ok is False
    assert "name cannot be empty" in err.lower()

    # Non-existent path
    ok, err, _ = pm.add_project("Proj", "/nonexistent/path/12345")
    assert ok is False
    assert "does not exist" in err.lower()

    # File path instead of directory
    temp_file = temp_config_dir / "somefile.txt"
    temp_file.write_text("hello")
    ok, err, _ = pm.add_project("Proj", str(temp_file))
    assert ok is False
    assert "not a directory" in err.lower()


def test_sorting_mru(temp_config_dir):
    p1 = Project(name="P1", path="/p1", last_opened="2026-07-20T10:00:00")
    p2 = Project(name="P2", path="/p2", last_opened="2026-07-28T10:00:00")
    p3 = Project(name="P3", path="/p3", last_opened=None)
    p4 = Project(name="P4", path="/p4", last_opened=None)

    sorted_projs = ProjectManager.sort_projects([p1, p3, p2, p4])
    assert [p.name for p in sorted_projs] == ["P2", "P1", "P3", "P4"]


def test_mark_as_opened(temp_config_dir):
    pm = ProjectManager(config_dir=temp_config_dir)
    test_dir = temp_config_dir / "proj1"
    test_dir.mkdir()

    _, _, p = pm.add_project("P1", str(test_dir))
    assert p.last_opened is None

    ts = pm.mark_as_opened(p)
    assert ts is not None
    
    loaded = pm.load_projects()
    assert loaded[0].last_opened == ts


def test_update_and_delete_project(temp_config_dir):
    pm = ProjectManager(config_dir=temp_config_dir)
    dir1 = temp_config_dir / "dir1"
    dir2 = temp_config_dir / "dir2"
    dir1.mkdir()
    dir2.mkdir()

    _, _, p1 = pm.add_project("Old Name", str(dir1))
    pm.mark_as_opened(p1)
    
    ok, err, updated = pm.update_project(p1, "New Name", str(dir2))
    assert ok is True
    assert updated.name == "New Name"
    assert updated.path == str(dir2.resolve())
    assert updated.last_opened is not None  # Preserved

    del_ok = pm.delete_project(updated)
    assert del_ok is True
    assert pm.load_projects() == []
