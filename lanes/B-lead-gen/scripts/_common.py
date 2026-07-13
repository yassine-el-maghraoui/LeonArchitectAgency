"""Helpers partagés par les scripts de lane B. Stdlib uniquement."""

import csv
import os
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = REPO_ROOT / "outputs" / "leads"


def load_env() -> None:
    """Charge .env du repo root dans os.environ (sans écraser l'existant)."""
    env_file = REPO_ROOT / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def require_key(name: str) -> str:
    load_env()
    value = os.environ.get(name, "")
    if not value:
        sys.exit(f"Erreur: {name} manquant. Copier .env.example vers .env et remplir.")
    return value


def output_path(slug: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR / f"{date.today().isoformat()}_{slug}.csv"


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} lignes -> {path}")
