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

YTDLP_PATH = Path(sys.executable).parent / "yt-dlp"
FFMPEG_PATH = BASE_DIR / "bin" / "ffmpeg"

FFMPEG_FORMAT = "s16le"
FFMPEG_SAMPLE_RATE = "48000"
FFMPEG_AUDIO_CHANNELS = "2"

CACHE_LIMIT = 20 * 1024 * 1024 * 1024
CACHE_PATH = Path(BASE_DIR).parent / "cache"
