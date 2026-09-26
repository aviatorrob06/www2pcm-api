from logging import DEBUG
from pathlib import Path
import logging
import sys

def configLogger():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

BASE_DIR = Path(__file__).parent

EXE_EXT = ""

YTDLP_PATH = BASE_DIR / "bin" / f"yt-dlp{EXE_EXT}"
FFMPEG_PATH = BASE_DIR / "bin" / f"ffmpeg{EXE_EXT}"
FFPROBE_PATH = BASE_DIR / "bin" / f"ffprobe{EXE_EXT}"

FFMPEG_FORMAT = "s16le"
FFMPEG_SAMPLE_RATE = "48000"
FFMPEG_AUDIO_CHANNELS = "2"

CACHE_LIMIT = 20 * 1024 * 1024 * 1024
CACHE_PATH = Path(BASE_DIR).parent / "cache"

DIRECT_URL_ALLOWED = False
