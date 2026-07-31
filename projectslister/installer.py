import os
import sys
from pathlib import Path
from typing import Tuple

BASH_FUNCTION_BLOCK = """
# Added by ProjectsLister
projls() {
    local tmpfile
    tmpfile=$(mktemp)
    projectslister > "$tmpfile"
    local target
    target=$(cat "$tmpfile")
    rm -f "$tmpfile"
    if [ -n "$target" ] && [ -d "$target" ]; then
        cd "$target" || return
    fi
}
"""

POWERSHELL_FUNCTION_BLOCK = """
# Added by ProjectsLister
function projls {
    $tmpfile = [System.IO.Path]::GetTempFileName()
    projectslister | Out-File -FilePath $tmpfile -Encoding utf8
    $target = (Get-Content $tmpfile -Raw).Trim()
    Remove-Item $tmpfile -ErrorAction SilentlyContinue
    if ($target -and (Test-Path $target)) {
        Set-Location $target
    }
}
"""


def detect_shell_and_profile() -> Tuple[str, Path]:
    if sys.platform.startswith("win"):
        user_profile = os.environ.get("USERPROFILE", str(Path.home()))
        ps_dir = Path(user_profile) / "Documents" / "WindowsPowerShell"
        profile_path = ps_dir / "Microsoft.PowerShell_profile.ps1"
        return "powershell", profile_path

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

    try:
        profile_path.parent.mkdir(parents=True, exist_ok=True)

        if profile_path.exists():
            content = profile_path.read_text(encoding="utf-8", errors="ignore")
            # If already contains old or new projls function, strip old version and update
            if "projls()" in content or "function projls" in content:
                # Replace old block if needed
                lines = content.splitlines()
                new_lines = []
                in_block = False
                for line in lines:
                    if "# Added by ProjectsLister" in line or "projls() {" in line or "function projls {" in line:
                        in_block = True
                        continue
                    if in_block:
                        if line.strip() == "}" or line.strip() == "fi}":
                            in_block = False
                        continue
                    new_lines.append(line)
                content = "\n".join(new_lines).rstrip() + "\n"
                profile_path.write_text(content, encoding="utf-8")

            backup_path = profile_path.with_name(profile_path.name + ".bak")
            backup_path.write_bytes(profile_path.read_bytes())

        function_block = POWERSHELL_FUNCTION_BLOCK if shell_type == "powershell" else BASH_FUNCTION_BLOCK

        with open(profile_path, "a", encoding="utf-8") as f:
            f.write("\n" + function_block.strip() + "\n")

        if shell_type == "powershell":
            reload_cmd = f". '{profile_path}'"
        else:
            reload_cmd = f"source {profile_path}"

        success_msg = (
            f"Successfully updated 'projls' shell function in {profile_path}!\n"
            f"Please run '{reload_cmd}' or open a new terminal window."
        )
        return True, success_msg

    except Exception as e:
        return False, f"Failed to update shell profile at {profile_path}: {e}"
