"""Runtime settings, read from environment variables"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

# backend/app/config.py -> parents[2] is the repository root.
_REPO_ROOT = Path(__file__).resolve().parents[2]


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    models_dir: Path = _REPO_ROOT / "models"
    cors_origins: list[str] = field(default_factory=lambda: ["http://localhost:3000"])
    max_body_bytes: int = 64 * 1024

    @classmethod
    def from_env(cls) -> "Settings":
        models_dir = os.environ.get("PHISH_MODELS_DIR")
        return cls(
            models_dir=Path(models_dir).expanduser().resolve() if models_dir else cls.models_dir,
            cors_origins=_split_csv(os.environ.get("PHISH_CORS_ORIGINS", "http://localhost:3000")),
            max_body_bytes=int(os.environ.get("PHISH_MAX_BODY_BYTES", 64 * 1024)),
        )
