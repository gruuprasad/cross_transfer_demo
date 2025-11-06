
import os
from pathlib import Path

# ------------------------------------------------------------
# Project paths
# ------------------------------------------------------------

def get_project_root() -> Path:
    """
    Returns the absolute path to the robot_lab_project root directory.
    Assumes this file lives in scripts/utils/scene_utils.py
    """
    return Path(__file__).resolve().parents[2]  # go up two levels


def ensure_folder_structure():
    """
    Creates the standard folder layout if it doesn't exist.
    """
    root = get_project_root()

    folders = [
        root / "assets" / "robots",
        root / "assets" / "props",
        root / "scenes",
#        root / "schemas" / "ai",
        root / "scripts" / "utils",
        root / "data" / "logs",
    ]

    for folder in folders:
        folder.mkdir(parents=True, exist_ok=True)

    print("✅ Project folder structure ready at:", root)


def get_usd_path(category: str, name: str) -> str:
    """
    Returns a full path to a USD file inside the project.
    Example:
        get_usd_path("scenes", "RobotLab.usda")
        get_usd_path("assets/robots", "Robot.usda")
    """
    root = get_project_root()
    return str(root / category / name)


if __name__ == "__main__":
    # Run this file directly to set up your project folders.
    ensure_folder_structure()

    # Example usage demo
    print(get_usd_path("assets/robots", "Robot.usda"))
