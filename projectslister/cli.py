import sys
from projectslister.app import ProjectsListerApp
from projectslister.installer import (
    install_shell_integration,
    is_shell_installed,
    detect_shell_and_profile,
)


def main() -> None:
    if "--install-shell" in sys.argv:
        success, msg = install_shell_integration()
        print(msg)
        sys.exit(0 if success else 1)

    if "--help" in sys.argv or "-h" in sys.argv:
        print("ProjectsLister (projls) - TUI project switcher")
        print("\nUsage:")
        print("  projectslister                 Run TUI app")
        print("  projectslister --install-shell  Install shell function 'projls' into your shell profile")
        print("  projectslister --help           Show this help message")
        sys.exit(0)

    _, profile_path = detect_shell_and_profile()
    if not is_shell_installed(profile_path):
        print(
            "Tip: Run 'projectslister --install-shell' to enable the 'projls' terminal command.",
            file=sys.stderr,
        )

    app = ProjectsListerApp()
    app.run()
    if app.selected_path:
        print(app.selected_path, flush=True)


if __name__ == "__main__":
    main()
