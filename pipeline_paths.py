"""Small shared helpers for running the existing pipeline per MOIL mine.

Raw public inputs and generated outputs are deliberately stored by mine.  This
prevents a dashboard selection from accidentally showing Dongri Buzurg data for
another mine.
"""
from pathlib import Path
import json


ROOT = Path(__file__).resolve().parent
MINES_FILE = ROOT / "backend" / "mines.json"


def get_mine(mine_id: str) -> dict:
    mines = json.loads(MINES_FILE.read_text(encoding="utf-8"))
    for mine in mines:
        if mine["id"] == mine_id:
            return mine
    raise ValueError(f"Unknown mine_id: {mine_id}")


def processed_dir(mine_id: str) -> Path:
    path = ROOT / "data" / "processed" / mine_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def model_path(mine_id: str, name: str) -> Path:
    path = ROOT / "models" / mine_id
    path.mkdir(parents=True, exist_ok=True)
    return path / name


def input_path(kind: str, mine_id: str, legacy_name: str) -> Path:
    """Use mine-scoped inputs; retain Dongri's committed legacy input files."""
    candidate = ROOT / "data" / kind / f"{mine_id}.csv"
    if candidate.exists():
        return candidate
    if mine_id == "dongri_buzurg":
        return ROOT / "data" / kind / legacy_name
    return candidate
