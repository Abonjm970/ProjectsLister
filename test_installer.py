
from projectslister.installer import install_shell_integration
from pathlib import Path

# Create a dummy profile
dummy_profile = Path("dummy_bashrc")
dummy_profile.write_text("# This is my bashrc")

success, msg = install_shell_integration(profile_override=dummy_profile)
print(f"Success: {success}")
print(f"Message: {msg}")
print(f"Content:\n{dummy_profile.read_text()}")
