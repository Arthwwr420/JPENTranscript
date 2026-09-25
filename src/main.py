from transcription.transcript import TranscriptorJPEN
from pathlib import Path

def main():
    inputdir = Path("../data/video")
    output_dir= Path("../data/output")

    transcript = TranscriptorJPEN(model_path="../models/", device="cuda", model_size="small")

    transcript.transcribe_dir(inputdir, output_dir)


if __name__ == '__main__':
    main()
