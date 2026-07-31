# ProjectsLister (projls)

**ProjectsLister** (or `projls`) is a fast, keyboard-driven Terminal User Interface (TUI) tool designed to help you quickly navigate between your most frequently used project directories from the command line.

## Why ProjectsLister?
- **Speed:** Quickly jump to projects without typing long `cd` paths.
- **Efficient:** Full keyboard control (no mouse needed).
- **Smart:** Automatically orders projects by "Most Recently Used" (MRU).
- **Integrated:** The `projls` command seamlessly changes your current terminal directory.

## Installation

### Prerequisites
- Python 3.10+
- `pipx` (Recommended for global tool installation)

### Steps

1. **Install the package:**
   ```bash
   pipx install .
   ```

2. **Enable Shell Integration:**
   Run the following command once to add the `projls` function to your shell profile (`~/.bashrc` or PowerShell profile):
   ```bash
   projectslister --install-shell
   ```
   *Note: Open a new terminal window or run `source ~/.bashrc` (on Linux/macOS) to activate the command.*

## Usage

Simply type `projls` in your terminal to open the TUI:

```bash
projls
```

### Keyboard Shortcuts
| Key | Action |
| :--- | :--- |
| `a` | Add a new project |
| `e` | Edit the selected project |
| `d` | Delete the selected project |
| `/` | Search projects |
| `Enter` | Open (navigate to) the selected project |
| `Esc` | Go back / Cancel |
| `q` | Quit |

## How it works
ProjectsLister saves you from manual path management. When you select a project in the TUI, it exits and prints the path, which is then captured by the `projls` shell function to execute the `cd` command in your current terminal session.
