import tempfile
from pathlib import Path
import pytest
from projectslister.app import ProjectsListerApp, ProjectFormModal, ConfirmModal
from projectslister.models import ProjectManager


@pytest.fixture
def temp_manager():
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = ProjectManager(config_dir=Path(tmpdir))
        yield manager


@pytest.mark.asyncio
async def test_app_empty_state(temp_manager):
    app = ProjectsListerApp(manager=temp_manager)
    async with app.run_test() as pilot:
        empty_state = app.query_one("#empty-state")
        assert empty_state.display is True


@pytest.mark.asyncio
async def test_app_add_project(temp_manager):
    test_dir = temp_manager.config_dir / "my_project"
    test_dir.mkdir()

    app = ProjectsListerApp(manager=temp_manager)
    async with app.run_test() as pilot:
        # Trigger add action
        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, ProjectFormModal)

        # Fill inputs
        input_name = app.screen.query_one("#input-name")
        input_path = app.screen.query_one("#input-path")
        
        input_name.value = "Awesome App"
        input_path.value = str(test_dir)
        
        # Click save button
        await pilot.click("#btn-save")
        await pilot.pause()

        # Modal closed, project added
        assert not isinstance(app.screen, ProjectFormModal)
        assert len(app.projects) == 1
        assert app.projects[0].name == "Awesome App"


@pytest.mark.asyncio
async def test_app_add_project_validation_error(temp_manager):
    app = ProjectsListerApp(manager=temp_manager)
    async with app.run_test() as pilot:
        await pilot.press("a")
        await pilot.pause()
        
        # Click save with empty inputs
        await pilot.click("#btn-save")
        await pilot.pause()
        
        # Modal remains open, error shown
        assert isinstance(app.screen, ProjectFormModal)


@pytest.mark.asyncio
async def test_app_search_filter(temp_manager):
    d1 = temp_manager.config_dir / "alpha"
    d2 = temp_manager.config_dir / "beta"
    d1.mkdir()
    d2.mkdir()

    temp_manager.add_project("Alpha Project", str(d1))
    temp_manager.add_project("Beta App", str(d2))

    app = ProjectsListerApp(manager=temp_manager)
    async with app.run_test() as pilot:
        await pilot.pause()
        assert len(app.filtered_projects) == 2

        # Press '/' to open search
        await pilot.press("slash")
        await pilot.pause()
        search_bar = app.query_one("#search-bar")
        assert search_bar.has_class("visible")

        # Search for alpha
        await pilot.press("a", "l", "p", "h", "a")
        await pilot.pause()
        assert len(app.filtered_projects) == 1
        assert app.filtered_projects[0].name == "Alpha Project"

        # Press Esc to clear search
        await pilot.press("escape")
        await pilot.pause()
        assert len(app.filtered_projects) == 2


@pytest.mark.asyncio
async def test_app_open_project(temp_manager):
    d1 = temp_manager.config_dir / "proj1"
    d1.mkdir()
    temp_manager.add_project("Proj 1", str(d1))

    app = ProjectsListerApp(manager=temp_manager)
    async with app.run_test() as pilot:
        await pilot.pause()
        # Press Enter to open currently highlighted project
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmModal)

        # Press 'y' to confirm
        await pilot.press("y")
        await pilot.pause()

    assert app.selected_path == str(d1.resolve())
    loaded = temp_manager.load_projects()
    assert loaded[0].last_opened is not None


@pytest.mark.asyncio
async def test_app_delete_project(temp_manager):
    d1 = temp_manager.config_dir / "to_delete"
    d1.mkdir()
    temp_manager.add_project("To Delete", str(d1))

    app = ProjectsListerApp(manager=temp_manager)
    async with app.run_test() as pilot:
        await pilot.pause()
        assert len(app.projects) == 1
        
        # Press 'd' to delete
        await pilot.press("d")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmModal)

        # Press 'y' to confirm delete
        await pilot.press("y")
        await pilot.pause()
        assert len(app.projects) == 0


@pytest.mark.asyncio
async def test_app_edit_project(temp_manager):
    d1 = temp_manager.config_dir / "orig"
    d2 = temp_manager.config_dir / "renamed"
    d1.mkdir()
    d2.mkdir()
    temp_manager.add_project("Original", str(d1))

    app = ProjectsListerApp(manager=temp_manager)
    async with app.run_test() as pilot:
        await pilot.pause()
        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, ProjectFormModal)

        input_name = app.screen.query_one("#input-name")
        input_path = app.screen.query_one("#input-path")

        input_name.value = "Renamed Project"
        input_path.value = str(d2)

        await pilot.click("#btn-save")
        await pilot.pause()

        assert len(app.projects) == 1
        assert app.projects[0].name == "Renamed Project"
        assert app.projects[0].path == str(d2.resolve())


@pytest.mark.asyncio
async def test_app_footer_buttons_click(temp_manager):
    app = ProjectsListerApp(manager=temp_manager)
    async with app.run_test() as pilot:
        await pilot.pause()
        
        # Click footer add button
        await pilot.click("#btn-footer-add")
        await pilot.pause()
        assert isinstance(app.screen, ProjectFormModal)

        # Cancel modal
        await pilot.press("escape")
        await pilot.pause()

        # Click footer search button
        await pilot.click("#btn-footer-search")
        await pilot.pause()
        assert app.query_one("#search-bar").has_class("visible")


@pytest.mark.asyncio
async def test_app_quit(temp_manager):
    app = ProjectsListerApp(manager=temp_manager)
    async with app.run_test() as pilot:
        await pilot.press("q")
        await pilot.pause()

    assert app.selected_path is None
