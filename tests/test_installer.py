import tempfile
from pathlib import Path
from projectslister.installer import (
    detect_shell_and_profile,
    is_shell_installed,
    install_shell_integration,
    BASH_FUNCTION_BLOCK,
)


def test_is_shell_installed(tmp_path):
    profile = tmp_path / ".bashrc"
    assert not is_shell_installed(profile)

    profile.write_text("# random config\nexport PATH=$PATH\n")
    assert not is_shell_installed(profile)

    profile.write_text(BASH_FUNCTION_BLOCK)
    assert is_shell_installed(profile)


def test_install_shell_integration(tmp_path):
    profile = tmp_path / ".bashrc"
    profile.write_text("# Initial bashrc\n")

    success, msg = install_shell_integration(profile_override=profile)
    assert success is True
    assert "Successfully installed" in msg

    # Verify backup created
    backup = tmp_path / ".bashrc.bak"
    assert backup.exists()
    assert backup.read_text() == "# Initial bashrc\n"

    # Verify function block appended
    new_content = profile.read_text()
    assert "projls()" in new_content
    assert "# Added by ProjectsLister" in new_content

    # Idempotency test (calling again should not duplicate)
    success2, msg2 = install_shell_integration(profile_override=profile)
    assert success2 is True
    assert "already installed" in msg2
