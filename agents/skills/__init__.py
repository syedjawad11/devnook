"""Load skill files as strings for injection into agent prompts."""
from pathlib import Path

SKILLS_DIR = Path(__file__).parent


def load_skill(name: str) -> str:
    """Load a skill file by name (without .md extension)."""
    path = SKILLS_DIR / f"{name}.md"
    return path.read_text(encoding="utf-8") if path.exists() else ""
