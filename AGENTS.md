# ProjectsLister (projls) Agent Instructions

## Installation & Setup
- **Installation:** Always install globally via `pipx` to ensure environment isolation and make the CLI tool available system-wide:
  ```bash
  pipx install .
  ```
- **Shell Integration:** The `projls` command is a shell function, not a binary. To enable it (which provides the `cd` functionality to the selected project), run:
  ```bash
  projectslister --install-shell
  ```
  This appends a function to `~/.bashrc` (or PowerShell profile) that wraps the `projectslister` CLI command.

## Architecture
- **Core Logic:** Located in `projectslister/`.
- **UI:** Built using [Textual](https://textual.textualize.io/). Entry point is `projectslister.cli:main`.
- **Data:** Persistent state is stored in `~/.config/projectslister/projects.json` (managed via `platformdirs`).
- **Integration:** The `projls` shell function is a shim. It executes the `projectslister` CLI, captures the output (target path), and performs the `cd` in the current shell. 
  - *Crucial Rule:* The TUI app *must not* execute `cd` itself. It merely prints the selected path to stdout upon exit.

## Development
- **Entry Point:** `projectslister/cli.py` handles CLI arguments (`--install-shell`) and invokes the Textual app.
- **Workflow:** When making changes, reinstall using `pipx install .` to reflect updates in the global environment.
- **Verification:** 
  - Ensure TUI exits cleanly before printing the target path to stdout.
  - If modifying shell integration, verify by re-running `projectslister --install-shell` and sourcing your shell profile.
