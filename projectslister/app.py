import os
from pathlib import Path
from typing import List, Optional, Tuple

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Footer, Header, Input, Label, OptionList, Static
from textual.widgets.option_list import Option

from projectslister.models import Project, ProjectManager


CSS = """
Screen {
    background: $surface;
}

#main-container {
    padding: 1 2;
    height: 1fr;
}

#search-bar {
    margin-bottom: 1;
    border: tall $accent;
    display: none;
}

#search-bar.visible {
    display: block;
}

#project-list {
    height: 1fr;
    border: round $primary;
    background: $surface;
}

#empty-state {
    text-align: center;
    color: $text-muted;
    padding: 3;
    content-align: center middle;
    height: 1fr;
    border: round $primary;
}

.modal-screen {
    align: center middle;
    background: rgba(0, 0, 0, 0.65);
}

.modal-box {
    width: 60;
    max-width: 90%;
    height: auto;
    background: $panel;
    border: thick $primary;
    padding: 1 2;
}

.modal-title {
    text-style: bold;
    color: $accent;
    margin-bottom: 1;
    text-align: center;
}

.modal-label {
    margin-top: 1;
    color: $text;
}

.modal-input {
    margin-top: 0;
    margin-bottom: 1;
}

.error-text {
    color: $error;
    margin-top: 1;
    margin-bottom: 1;
    min-height: 1;
}

.button-row {
    margin-top: 1;
    align: right middle;
    height: auto;
}

.button-row Button {
    margin-left: 1;
}

#confirm-message {
    margin-top: 1;
    margin-bottom: 1;
    text-align: center;
}
"""


def format_display_path(path_str: str) -> str:
    try:
        home = str(Path.home())
        if path_str == home:
            return "~"
        elif path_str.startswith(home + os.sep):
            return "~" + path_str[len(home):]
    except Exception:
        pass
    return path_str


class ProjectFormModal(ModalScreen[Optional[Tuple[str, str]]]):
    DEFAULT_CSS = CSS

    def __init__(self, title: str, project: Optional[Project] = None):
        super().__init__(classes="modal-screen")
        self.form_title = title
        self.project = project

    def compose(self) -> ComposeResult:
        with Container(classes="modal-box"):
            yield Label(self.form_title, classes="modal-title")
            
            yield Label("Project Name:", classes="modal-label")
            initial_name = self.project.name if self.project else ""
            yield Input(value=initial_name, placeholder="e.g. My Project", id="input-name", classes="modal-input")
            
            yield Label("Project Path:", classes="modal-label")
            initial_path = self.project.path if self.project else ""
            yield Input(value=initial_path, placeholder="e.g. ~/projects/my-project", id="input-path", classes="modal-input")
            
            yield Label("", id="error-message", classes="error-text")
            
            with Horizontal(classes="button-row"):
                yield Button("Save", variant="primary", id="btn-save")
                yield Button("Cancel", variant="default", id="btn-cancel")

    def on_mount(self) -> None:
        self.query_one("#input-name", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-save":
            self.submit_form()
        elif event.button.id == "btn-cancel":
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "input-name":
            self.query_one("#input-path", Input).focus()
        elif event.input.id == "input-path":
            self.submit_form()

    def key_escape(self) -> None:
        self.dismiss(None)

    def submit_form(self) -> None:
        name = self.query_one("#input-name", Input).value.strip()
        path_str = self.query_one("#input-path", Input).value.strip()

        ok_name, err_name = ProjectManager.validate_name(name)
        if not ok_name:
            self.query_one("#error-message", Label).update(err_name)
            self.query_one("#input-name", Input).focus()
            return

        ok_path, err_path = ProjectManager.validate_path(path_str)
        if not ok_path:
            self.query_one("#error-message", Label).update(err_path)
            self.query_one("#input-path", Input).focus()
            return

        self.dismiss((name, path_str))


class ConfirmModal(ModalScreen[bool]):
    DEFAULT_CSS = CSS

    BINDINGS = [
        Binding("y", "confirm", "Yes", show=False),
        Binding("n", "cancel", "No", show=False),
    ]

    def __init__(self, title: str, message: str, is_danger: bool = False):
        super().__init__(classes="modal-screen")
        self.confirm_title = title
        self.message = message
        self.is_danger = is_danger

    def compose(self) -> ComposeResult:
        variant = "error" if self.is_danger else "primary"
        with Container(classes="modal-box"):
            yield Label(self.confirm_title, classes="modal-title")
            yield Label(self.message, id="confirm-message")
            with Horizontal(classes="button-row"):
                yield Button("Yes [y]", variant=variant, id="btn-yes")
                yield Button("No [n]", variant="default", id="btn-no")

    def on_mount(self) -> None:
        self.query_one("#btn-yes", Button).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-yes":
            self.dismiss(True)
        elif event.button.id == "btn-no":
            self.dismiss(False)

    def action_confirm(self) -> None:
        self.dismiss(True)

    def action_cancel(self) -> None:
        self.dismiss(False)

    def key_escape(self) -> None:
        self.dismiss(False)


class EmptyState(Static):
    can_focus = True


class ProjectsListerApp(App[Optional[str]]):
    TITLE = "ProjectsLister"
    DEFAULT_CSS = CSS

    BINDINGS = [
        Binding("a", "add_project", "add", show=True),
        Binding("e", "edit_project", "edit", show=True),
        Binding("d", "delete_project", "delete", show=True),
        Binding("slash", "focus_search", "search", show=True),
        Binding("enter", "open_project", "open", show=True),
        Binding("escape", "clear_search_or_back", "back", show=True),
        Binding("q", "quit_app", "quit", show=True),
    ]

    def __init__(self, manager: Optional[ProjectManager] = None):
        super().__init__()
        self.manager = manager or ProjectManager()
        self.projects: List[Project] = []
        self.filtered_projects: List[Project] = []
        self.selected_path: Optional[str] = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Container(id="main-container"):
            yield Input(placeholder="Type to search by name or path...", id="search-bar")
            yield OptionList(id="project-list")
            yield EmptyState("No projects found. Press 'a' to add a project.", id="empty-state")
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_project_list()

    def refresh_project_list(self, select_project: Optional[Project] = None) -> None:
        self.projects = self.manager.load_projects()
        self.apply_filter(select_project=select_project)

    def apply_filter(self, select_project: Optional[Project] = None) -> None:
        search_bar = self.query_one("#search-bar", Input)
        query = search_bar.value.strip().lower()

        if query:
            self.filtered_projects = [
                p for p in self.projects
                if query in p.name.lower() or query in p.path.lower()
            ]
        else:
            self.filtered_projects = list(self.projects)

        option_list = self.query_one("#project-list", OptionList)
        empty_state = self.query_one("#empty-state", Static)

        option_list.clear_options()

        if not self.filtered_projects:
            option_list.display = False
            empty_state.display = True
            if query:
                empty_state.update(f"No projects matching '{query}'. Press 'Esc' to clear search.")
            else:
                empty_state.update("No projects found. Press 'a' to add a project.")
            if self.focused is not search_bar:
                empty_state.focus()
        else:
            option_list.display = True
            empty_state.display = False

            select_idx = 0
            for idx, p in enumerate(self.filtered_projects):
                disp_path = format_display_path(p.path)
                prompt = f"[bold cyan]{p.name}[/bold cyan]  [dim]({disp_path})[/dim]"
                option_list.add_option(Option(prompt, id=str(idx)))
                if select_project and p.name == select_project.name and p.path == select_project.path:
                    select_idx = idx

            option_list.highlighted = select_idx
            if self.focused is not search_bar:
                option_list.focus()

    def get_currently_selected_project(self) -> Optional[Project]:
        option_list = self.query_one("#project-list", OptionList)
        if option_list.highlighted is not None and 0 <= option_list.highlighted < len(self.filtered_projects):
            return self.filtered_projects[option_list.highlighted]
        return None

    def action_add_project(self) -> None:
        def on_add_done(result: Optional[Tuple[str, str]]) -> None:
            if result:
                name, path_str = result
                ok, err, new_proj = self.manager.add_project(name, path_str)
                if ok:
                    self.refresh_project_list(select_project=new_proj)
                else:
                    self.notify(err, severity="error")

        self.push_screen(ProjectFormModal("Add Project"), on_add_done)

    def action_edit_project(self) -> None:
        proj = self.get_currently_selected_project()
        if not proj:
            self.notify("No project selected to edit.", severity="warning")
            return

        def on_edit_done(result: Optional[Tuple[str, str]]) -> None:
            if result:
                new_name, new_path_str = result
                ok, err, updated_proj = self.manager.update_project(proj, new_name, new_path_str)
                if ok:
                    self.refresh_project_list(select_project=updated_proj)
                else:
                    self.notify(err, severity="error")

        self.push_screen(ProjectFormModal("Edit Project", project=proj), on_edit_done)

    def action_delete_project(self) -> None:
        proj = self.get_currently_selected_project()
        if not proj:
            self.notify("No project selected to delete.", severity="warning")
            return

        def on_delete_done(confirmed: bool) -> None:
            if confirmed:
                self.manager.delete_project(proj)
                self.refresh_project_list()

        msg = f"Are you sure you want to delete '{proj.name}'?"
        self.push_screen(ConfirmModal("Delete Project", msg, is_danger=True), on_delete_done)

    def action_open_project(self) -> None:
        proj = self.get_currently_selected_project()
        if not proj:
            self.notify("No project selected to open.", severity="warning")
            return

        def on_open_done(confirmed: bool) -> None:
            if confirmed:
                self.manager.mark_as_opened(proj)
                self.selected_path = proj.path
                self.exit(0)

        msg = f"Open '{proj.name}'?"
        self.push_screen(ConfirmModal("Open Project", msg, is_danger=False), on_open_done)

    def action_focus_search(self) -> None:
        search_bar = self.query_one("#search-bar", Input)
        search_bar.add_class("visible")
        search_bar.focus()

    def action_clear_search_or_back(self) -> None:
        search_bar = self.query_one("#search-bar", Input)
        if search_bar.value != "" or search_bar.has_class("visible"):
            search_bar.value = ""
            search_bar.remove_class("visible")
            self.apply_filter()
        
        option_list = self.query_one("#project-list", OptionList)
        if option_list.display:
            option_list.focus()

    def action_quit_app(self) -> None:
        self.selected_path = None
        self.exit(0)

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search-bar":
            self.apply_filter()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.action_open_project()
