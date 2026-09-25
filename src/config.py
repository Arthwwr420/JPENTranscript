"""Load config.yaml and point local caches at models/ so nothing reaches
the network once weights are downloaded."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from dataclasses import dataclass

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass
class WhisperConfig:
    model_size: str
    model_path: str
    device: str
    compute_type: str



@dataclass
class AppConfig:
    whisper: WhisperConfig
    output_path:  Path
    language: str
    srt: bool
    overwrite: bool
    model_cache_dir: Path

#    translation: TranslationConfig
    


def load_config(path: Path | None = None) -> AppConfig:
    path = path or REPO_ROOT / "config.yaml"
    raw = yaml.safe_load(path.read_text())

    cache_dir = REPO_ROOT / raw["cache_dir"]
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Route Hugging Face's cache into our local models/ dir so everything
    # lives in one place and offline mode is predictable.
    os.environ.setdefault("HF_HOME", str(cache_dir))

    return AppConfig(
        whisper=WhisperConfig(**raw["whisper"]),
        model_cache_dir=cache_dir,
        output_path=raw.get("output_path"),
        language=raw.get("language"),
        srt=raw.get("srt")or False,
        overwrite=raw.get("overwrite") or False
    )


