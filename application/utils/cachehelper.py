import json
import os
import time
import logging
from pathlib import Path
from application.config import BASE_DIR, configLogger, CACHE_PATH, CACHE_LIMIT

configLogger()
logger = logging.getLogger(__name__)

def mark_used(path: Path):
    now = time.time()
    os.utime(path, (now, now))

def lru_sweep(bytes_needed: int):
    logger.debug("Checking if there is space in the cache for file about to be written")
    files = []

    total_size = 0

    for file in CACHE_PATH.rglob("*"):
        if file.is_file():
            size = file.stat().st_size

            total_size += size

            files.append(file)

    free_after_write = CACHE_LIMIT - total_size

    if free_after_write >= bytes_needed:
        return

    files.sort(key=lambda f: f.stat().st_mtime)

    for file in files:
        size = file.stat().st_size

        file.unlink()

        total_size-= size

        if CACHE_LIMIT - total_size >= bytes_needed:
            break

def save_metadata(video_id: str, metadata: dict):
    logger.debug(f"Saving metadata for {video_id}")

    path = CACHE_PATH / "metadata" / f"{video_id}.json"

    lru_sweep(
        len(
            json.dumps(metadata).encode("utf-8")
        )
    )

    with open(path, "w") as file:
        json.dump(metadata, file, indent=4)

    mark_used(path)

def read_metadata(video_id: str):
    logger.debug(f"Attempting to read metadata for {video_id}")
    path = CACHE_PATH / "metadata" / f"{video_id}.json"

    if not path.exists():
        raise FileNotFoundError("Not cached yet")
    with open(path, "r") as file:
        mark_used(path)
        return json.load(file)

def save_pcm(video_id: str, pcm_data):
    logger.debug(f"Attempting to save PCM file in cache for {video_id}")
    path = CACHE_PATH / "pcm" / f"{video_id}.pcm"

    lru_sweep(len(pcm_data))

    with open(path, "wb") as file:
        file.write(pcm_data)

    mark_used(path)

def read_pcm(video_id: str):
    path = CACHE_PATH / "pcm" / f"{video_id}.pcm"

    if not path.exists():
        raise FileNotFoundError("Not cached yet")

    with open(path, "rb") as file:
        mark_used(path)
        return file.read()