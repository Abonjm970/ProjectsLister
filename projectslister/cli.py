import sys
from projectslister.app import ProjectsListerApp


def main() -> None:
    app = ProjectsListerApp()
    app.run()
    if app.selected_path:
        print(app.selected_path, flush=True)


if __name__ == "__main__":
    main()
