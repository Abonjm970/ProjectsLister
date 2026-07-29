from dataclasses import dataclass, asdict
from datetime import datetime
import json
import os
from pathlib import Path
from typing import List, Optional, Tuple
import platformdirs


@dataclass
class Project:
    name: str
    path: str
    last_opened: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        return cls(
            name=data.get("name", ""),
            path=data.get("path", ""),
            last_opened=data.get("last_opened"),
        )


class ProjectManager:
    def __init__(self, config_dir: Optional[Path] = None):
        if config_dir is None:
            config_dir = Path(platformdirs.user_config_dir("projectslister"))
        self.config_dir = config_dir
        self.file_path = self.config_dir / "projects.json"

    def ensure_config_dir(self) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def load_projects(self) -> List[Project]:
        if not self.file_path.exists():
            return []
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    return []
                projects = [Project.from_dict(item) for item in data if isinstance(item, dict)]
                return self.sort_projects(projects)
        except (json.JSONDecodeError, OSError):
            return []

    def save_projects(self, projects: List[Project]) -> None:
        self.ensure_config_dir()
        temp_path = self.file_path.with_suffix(".json.tmp")
        data = [project.to_dict() for project in projects]
        
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())

        os.replace(temp_path, self.file_path)

    @staticmethod
    def sort_projects(projects: List[Project]) -> List[Project]:
        """
        Sort projects by MRU (most recently used first).
        Projects with last_opened=None are placed at the end while preserving relative insertion order.
        """
        def sort_key(item: Tuple[int, Project]):
            idx, proj = item
            if proj.last_opened is None:
                # Use tuple (0, "", -idx) so non-opened items preserve insertion order when reverse=True
                return (0, "", -idx)
            # Use tuple (1, date_str, -idx) for opened items (if date_str identical, preserve order)
            return (1, proj.last_opened, -idx)

        # Pair with original index to ensure stable sorting
        indexed = list(enumerate(projects))
        indexed.sort(key=sort_key, reverse=True)
        
        result = [proj for idx, proj in indexed]
        return result

    @staticmethod
    def validate_name(name: str) -> Tuple[bool, str]:
        stripped = name.strip()
        if not stripped:
            return False, "Project name cannot be empty."
        return True, ""

    @staticmethod
    def validate_path(path_str: str) -> Tuple[bool, str]:
        stripped = path_str.strip()
        if not stripped:
            return False, "Project path cannot be empty."
        
        expanded = Path(stripped).expanduser()
        if not expanded.exists():
            return False, f"Path does not exist: {stripped}"
        if not expanded.is_dir():
            return False, f"Path is not a directory: {stripped}"
        
        return True, ""

    @staticmethod
    def resolve_path(path_str: str) -> str:
        return str(Path(path_str.strip()).expanduser().resolve())

    def add_project(self, name: str, path_str: str) -> Tuple[bool, str, Optional[Project]]:
        valid_name, err_name = self.validate_name(name)
        if not valid_name:
            return False, err_name, None

        valid_path, err_path = self.validate_path(path_str)
        if not valid_path:
            return False, err_path, None

        resolved_path = self.resolve_path(path_str)
        projects = self.load_projects()

        new_project = Project(
            name=name.strip(),
            path=resolved_path,
            last_opened=None
        )
        projects.append(new_project)
        sorted_projects = self.sort_projects(projects)
        self.save_projects(sorted_projects)
        return True, "", new_project

    def update_project(self, old_project: Project, new_name: str, new_path_str: str) -> Tuple[bool, str, Optional[Project]]:
        valid_name, err_name = self.validate_name(new_name)
        if not valid_name:
            return False, err_name, None

        valid_path, err_path = self.validate_path(new_path_str)
        if not valid_path:
            return False, err_path, None

        resolved_path = self.resolve_path(new_path_str)
        projects = self.load_projects()

        target_idx = None
        for i, p in enumerate(projects):
            if p.name == old_project.name and p.path == old_project.path:
                target_idx = i
                break

        if target_idx is None:
            return False, "Project not found.", None

        updated_project = Project(
            name=new_name.strip(),
            path=resolved_path,
            last_opened=projects[target_idx].last_opened  # Keep original last_opened
        )
        projects[target_idx] = updated_project
        sorted_projects = self.sort_projects(projects)
        self.save_projects(sorted_projects)
        return True, "", updated_project

    def delete_project(self, project: Project) -> bool:
        projects = self.load_projects()
        filtered = [p for p in projects if not (p.name == project.name and p.path == project.path)]
        if len(filtered) == len(projects):
            return False
        self.save_projects(filtered)
        return True

    def mark_as_opened(self, project: Project) -> str:
        now_str = datetime.now().isoformat(timespec="seconds")
        projects = self.load_projects()
        
        for p in projects:
            if p.name == project.name and p.path == project.path:
                p.last_opened = now_str
                break
        
        sorted_projects = self.sort_projects(projects)
        self.save_projects(sorted_projects)
        return now_str
