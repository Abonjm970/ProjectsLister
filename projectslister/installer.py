import os
import sys
from pathlib import Path
from typing import Tuple

BASH_FUNCTION_BLOCK = """
# Added by ProjectsLister
projls() {
    local target
    target=$(projectslister)
    if [ -n "$target" ]; then
        cd "$target" || return
    fi
}
"""

POWERSHELL_FUNCTION_BLOCK = """
# Added by ProjectsLister
function projls {
    $target = projectslister
    if ($target) {
        Set-Location $target
    }
}
"""


def detect_shell_and_profile() -> Tuple[str, Path]:
    if sys.platform.startswith("win"):
        # Windows PowerShell Profile path
        user_profile = os.environ.get("USERPROFILE", str(Path.home()))
        ps_dir = Path(user_profile) / "Documents" / "WindowsPowerShell"
        profile_path = ps_dir / "Microsoft.PowerShell_profile.ps1"
        return "powershell", profile_path

    # Linux / Unix / macOS
    shell_env = os.environ.get("SHELL", "")
    home = Path.home()

    if "zsh" in shell_env:
        return "zsh", home / ".zshrc"
    
    return "bash", home / ".bashrc"


def is_shell_installed(profile_path: Path) -> bool:
    if not profile_path.exists():
        return False
    try:
        content = profile_path.read_text(encoding="utf-8", errors="ignore")
        return "projls()" in content or "function projls" in content
    except OSError:
        return False


def install_shell_integration(profile_override: Path = None) -> Tuple[bool, str]:
    shell_type, default_profile_path = detect_shell_and_profile()
    profile_path = profile_override or default_profile_path

    if is_shell_installed(profile_path):
        return True, f"Shell integration is already installed in {profile_path}"

    try:
        # Create parent directories if they don't exist
        profile_path.parent.mkdir(parents=True, exist_ok=True)

        # Create backup if file exists
        if profile_path.exists():
            backup_path = profile_path.with_name(profile_path.name + ".bak")
            backup_path.write_bytes(profile_path.read_bytes())

        # Select function block based on shell type
        function_block = POWERSHELL_FUNCTION_BLOCK if shell_type == "powershell" else BASH_FUNCTION_BLOCK

        # Append to profile file safely
        with open(profile_path, "a", encoding="utf-8") as f:
            f.write("\n" + function_block.strip() + "\n")

        if shell_type == "powershell":
            reload_cmd = f". '{profile_path}'"
        else:
            reload_cmd = f"source {profile_path}"

        success_msg = (
            f"Successfully installed 'projls' shell function into {profile_path}!\n"
            f"Please run '{reload_cmd}' or open a new terminal window to activate the 'projls' command."
        )
        return True, success_msg

    except Exception as e:
        return False, f"Failed to update shell profile at {profile_path}: {e}"
