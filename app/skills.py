import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict


@dataclass(frozen=True)
class SkillSpec:
    skill_id: str
    description: str
    prompt_template: str
    version: str = "1.0.0"


def load_skills(directory: str) -> Dict[str, SkillSpec]:
    root = Path(directory)
    if not root.exists() or not root.is_dir():
        raise ValueError(f"Skills directory does not exist: {directory}")

    skills: Dict[str, SkillSpec] = {}
    files = sorted(path for path in root.glob("*.json") if path.is_file())
    if not files:
        raise ValueError(f"No skill json files found in {directory}")

    for file_path in files:
        payload = _load_json(file_path)
        skill_id = str(payload.get("skill_id", "")).strip()
        if not skill_id:
            raise ValueError(f"Missing skill_id in {file_path}")
        prompt_template = str(payload.get("prompt_template", "")).strip()
        if not prompt_template:
            raise ValueError(f"Missing prompt_template in {file_path}")
        description = str(payload.get("description", "")).strip()
        version = str(payload.get("version", "1.0.0")).strip() or "1.0.0"
        skills[skill_id] = SkillSpec(
            skill_id=skill_id,
            description=description,
            prompt_template=prompt_template,
            version=version,
        )
    return skills


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON format: {path}: {exc}") from exc

