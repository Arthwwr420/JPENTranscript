"""CLI wrapper for TranscriptorJPEN.

Bypasses WhisperConfig on purpose (model_path/model_size/device passed
directly) so this CLI doesn't need to know your config.py internals. Swap
in `WhisperConfig(...)` later if you'd rather drive it from a config file.
"""

from __future__ import annotations

from pathlib import Path

import click

from transcription.transcript import TranscriptorJPEN
from config import AppConfig, load_config


@click.command()
@click.argument("input_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "-o", "--output", "output_path",
    type=click.Path(path_type=Path),
    default=None,
    help="Output directory. Defaults to alongside the input file(s).",
)
@click.option(
    "-l", "--language",
    default=None,
    type=click.Choice(["en", "ja"], case_sensitive=False),
    help="Force source language. Omit to let Whisper auto-detect per file.",
)
@click.option(
    "--model-size",
    default="medium",
    help="Whisper model size: tiny | base | small | medium | large-v3.",
)
@click.option(
    "--model-path",
    default="models/",
    help="Local directory to download/cache model weights (download_root).",
)
@click.option(
    "--device",
    default="cuda",
    type=click.Choice(["cpu", "cuda"]),
    help="Inference device.",
)
@click.option("--srt/--no-srt", default=False, help="Also write a .srt subtitle file.")
@click.option(
    "--overwrite/--no-overwrite",
    default=False,
    help="Re-transcribe files that already have output (directory mode only).",
)
@click.option(
    "--translate",
    is_flag=True,
    help="Reserved for future use: translate the transcript after transcribing.",
)
@click.option(
    "-c", "--config", "configfile",
    type=click.Path(path_type=Path),
    default=None,
    help="Configuration file (config.yaml) -> Override any other setting",
)

def main(
    input_path: Path,
    output_path: Path | None,
    language: str | None,
    model_size: str,
    model_path: str,
    device: str,
    srt: bool,
    overwrite: bool,
    translate: bool,
    configfile: Path | None,
):

    if configfile is not None:
        config = load_config(configfile)
        language = config.language 
        srt = config.srt or False
        overwrite = config.overwrite or False
        print(overwrite)
        
        transcriptor = TranscriptorJPEN(config.whisper)

    else:
        transcriptor = TranscriptorJPEN(
        model_size=model_size,
        model_path=model_path,
        device=device,
        )

    if input_path.is_dir():
        transcriptor.transcribe_dir(
            input_dir=input_path,
            output_dir=output_path,
            language=language,
            overwrite=overwrite,
            srt=srt,
        )
    else:
        # Single file
        base_out = transcriptor._build_output_paths(input_path, input_path.parent, output_path)
        transcriptor.transcribe_file(input_path, base_out, language, write_srt=srt)


if __name__ == "__main__":
    main()
