# ProjectsLister (projls) Agent Instructions

## ⚠️ Security & Restrictions
- **NEVER read or access `PRD.md`**. This file is strictly off-limits for all agent operations.

## Purpose
ProjectsLister is a fast, keyboard-driven TUI project switcher. 

## Development Workflow
- **Code:** All source code resides in `projectslister/`.
- **UI Framework:** Uses [Textual](https://textual.textualize.io/).
- **Testing:** Add tests to `tests/`. Ensure new features don't break the shell integration contract.
- **Workflow:** When editing, reinstall locally to reflect changes in the environment:
  ```bash
  pipx reinstall .
  ```
- **Shell Integration:** The `projls` command is a shell shim. 
  - *Constraint:* The Python app **must** print the selected path to `stdout` only *after* the TUI app exits. It must *not* attempt `cd` itself.
  - To test changes to shell integration:
    ```bash
    projectslister --install-shell
    source ~/.bashrc  # or ~/.zshrc
    ```

## Publishing
- **Versioning:** Update `version` in `pyproject.toml`.
- **Build:**
  ```bash
  rm -rf dist/ build/
  python -m build
  ```
- **Upload:**
  ```bash
  python -m twine upload dist/*
  ```
  - Requires `twine` installed in the dev environment. Use the API token from PyPI as password (username `__token__`).

## Key Files & Structure
- `projectslister/cli.py`: Main entry point. Handles `--install-shell` and launches the TUI.
- `projectslister/app.py`: Contains the `ProjectsListerApp` (Textual app) and CSS.
- `projectslister/installer.py`: Logic for modifying shell configuration files (`.bashrc`, PowerShell profiles).
- `~/.config/projectslister/projects.json`: Persistent project data.

## Operational Gotchas
- Always test TUI exit behavior. If it crashes or doesn't print the path to `stdout`, the `projls` shell function won't be able to change directories.
- Ensure CSS definitions in `app.py` use valid Textual markup syntax to avoid `MarkupError` at runtime.
