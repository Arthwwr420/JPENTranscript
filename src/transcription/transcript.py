from faster_whisper import WhisperModel
from .config import WhisperConfig

import sys
import os
import time
import json
from pathlib import Path

from dataclasses import dataclass

@dataclass
class Segment:
    start : float
    end: float
    text: str
    lan: str

class TranscriptorJPEN():
    def __init__(self, 
                 config : WhisperConfig|None = None,
                 model_path : str = "",
                 model_size : str = "", 
                 device : str = "",
                 ):
        """
        Transcriptor:
        Main class in charge of transcripting the sudio files
        If not None, config will overwrite the rest of the arguments
        
        """
        if config is not None:
            device = config.device
            model_path = config.model_path
        if model_path == "" or device == "" or model_size == "":
            raise ValueError("Empty model path or device")
        
        self._model = None
        self.device = device
        self.set_model(model_size, model_path)

   
    def _build_output_paths(self, mp4_path: Path, input_dir: Path, output_dir: Path | None):
        """
        Returns the output path of the text file

        If output_dir is None, files will be saved to the same dir as mp4_path
        """
        if output_dir is None:
            base = mp4_path.with_suffix("")
        else:
            relative = mp4_path.relative_to(input_dir)
            dest_dir = output_dir / relative.parent
            dest_dir.mkdir(parents=True, exist_ok=True)
            base = dest_dir / mp4_path.stem
        return base

    def _format_srt_timestamp(self, seconds: float) -> str:
        """
        Returns the timestamp in format
        "HH:MM:SS:MS"
        """
        ms = int(round(seconds * 1000))
        h, ms = divmod(ms, 3_600_000)
        m, ms = divmod(ms, 60_000)
        s, ms = divmod(ms, 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


    def set_model(self,
                  size, 
                  model_path : str,
                  ):
        """
        Sets the model
        """
        self._model = WhisperModel(
                model_size_or_path=size,
                device=self.device,
                download_root=model_path,
                )
                                         
    
    def transcribe_file(self, mp4_path: Path, base_out: Path,
                         language: str | None, write_srt: bool = False):
        """
        Transcribe single mp4 file into output.txt, also write JSON file
        with information about the language, input file, transcription time and
        segments

        :param mp4_path: Path to the input video
        :param base_out: Path to the output directory
        :param language: If we know the language (en or jp), else None
        :param write_srt: Toggle srt file writing (default False)

        """
        print(f"  -> Transcribing: {mp4_path.name}")
        t0 = time.time()

        segments_gen, info = self._model.transcribe(
            str(mp4_path),
            language=language,
            vad_filter=True,  # filtra silencios largos, ayuda con audio de reuniones/llamadas
        )

        segments = []
        full_text_parts = []
        for seg in segments_gen:
            segments.append({
                "start": round(seg.start, 3),
                "end": round(seg.end, 3),
                "text": seg.text.strip(),
            })
            full_text_parts.append(seg.text.strip())

        elapsed = time.time() - t0
        detected_lang = info.language
        lang_prob = round(info.language_probability, 3)

        # .txt con el texto plano
        txt_path = base_out.with_suffix(".txt")
        txt_path.write_text("\n".join(full_text_parts), encoding="utf-8")

        # .json con segmentos + metadata
        json_path = base_out.with_suffix(".json")
        json_data = {
            "source_file": str(mp4_path),
            "language": detected_lang,
            "language_probability": lang_prob,
            "duration_seconds": round(info.duration, 3),
            "transcription_time_seconds": round(elapsed, 2),
            "segments": segments,
        }
        json_path.write_text(
            json.dumps(json_data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        # .srt opcional
        if write_srt:
            srt_path = base_out.with_suffix(".srt")
            lines = []
            for i, seg in enumerate(segments, start=1):
                lines.append(str(i))
                lines.append(
                    f"{format_srt_timestamp(seg['start'])} --> {format_srt_timestamp(seg['end'])}"
                )
                lines.append(seg["text"])
                lines.append("")
            srt_path.write_text("\n".join(lines), encoding="utf-8")

        print(f"     idioma: {detected_lang} (prob {lang_prob})  |  "
              f"duracion audio: {info.duration:.1f}s  |  tiempo: {elapsed:.1f}s")
        print(f"     guardado: {txt_path.name}, {json_path.name}"
              + (f", {srt_path.name}" if write_srt else ""))


    def transcribe_dir(self, input_dir: Path, output_dir: Path | None=None,
                       language: str | None=None, 
                       overwrite : bool = False,
                       srt: bool = False,
                       ):
        if not input_dir.is_dir():
            print(f"ERROR: la carpeta no existe: {input_dir}")
            sys.exit(1)

        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)

        print(f"Buscando archivos .mp4 en: {input_dir}")
        mp4_files = sorted(input_dir.rglob("*.mp4"))

        if not mp4_files:
            print("No se encontraron archivos .mp4.")
            return

        print(f"Encontrados {len(mp4_files)} archivo(s) .mp4.\n")

        processed, skipped, failed = 0, 0, 0

        for mp4_path in mp4_files:
            base_out = self._build_output_paths(mp4_path, input_dir, output_dir)
            txt_path = base_out.with_suffix(".txt")

            if txt_path.exists() and not overwrite:
                print(f"  (saltado, ya existe) {mp4_path.name}")
                skipped += 1
                continue

            try:
                self.transcribe_file(mp4_path, base_out, language, srt)
                processed += 1
            except Exception as e:
                print(f"  !! ERROR transcribiendo {mp4_path.name}: {e}")
                failed += 1

        print("\n--- Resumen ---")
        print(f"Transcritos: {processed}")
        print(f"Saltados (ya existian): {skipped}")
        print(f"Fallidos: {failed}")
