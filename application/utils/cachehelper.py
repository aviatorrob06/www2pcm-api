import json
import os
import time
import logging
import hashlib
from application.utils.source_enum import SourceType
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

def save_metadata(source: SourceType, id: str, metadata: dict):
    logger.debug(f"Saving metadata for source type {source}, id {id}")

    if source == SourceType.SOUNDCLOUD or source == SourceType.BANDCAMP:
        id = id.replace("/", "_")

    path = CACHE_PATH / source.value / "metadata" / f"{id}.json"

    lru_sweep(
        len(
            json.dumps(metadata).encode("utf-8")
        )
    )

    with open(path, "w") as file:
        json.dump(metadata, file, indent=4)

    mark_used(path)

def read_metadata(source: SourceType, id: str):
    logger.debug(f"Attempting to read metadata for source {source}, id {id}")

    if source == SourceType.SOUNDCLOUD or source == SourceType.BANDCAMP:
        id = id.replace("/", "_")

    path = CACHE_PATH / source.value / "metadata" / f"{id}.json"

    if not path.exists():
        raise FileNotFoundError("Not cached yet")
    with open(path, "r") as file:
        mark_used(path)
        return json.load(file)

def save_pcm(source: SourceType, id: str, pcm_data):
    logger.debug(f"Attempting to save PCM file in cache for source {source}, id {id}")

    if source == SourceType.SOUNDCLOUD or source == SourceType.BANDCAMP:
        id = id.replace("/", "_")

    path = CACHE_PATH / source.value / "pcm" / f"{id}.pcm"

    lru_sweep(len(pcm_data))

    with open(path, "wb") as file:
        file.write(pcm_data)

    mark_used(path)

def read_pcm(source: SourceType, id: str):
    if source == SourceType.SOUNDCLOUD or source == SourceType.BANDCAMP:
        id = id.replace("/", "_")

    path = CACHE_PATH / source.value / "pcm" / f"{id}.pcm"

    if not path.exists():
        raise FileNotFoundError("Not cached yet")

    with open(path, "rb") as file:
        mark_used(path)
        return file.read()

def save_ytlink(source: SourceType, track_id: str, video_id: str):
    logger.debug(f"Attempting to save ytlink for source {source}, id {track_id}")
    if source.value == SourceType.SPOTIFY.value:

        path = CACHE_PATH / source.value / "yt-links" / f"{track_id}.json"

        data = {"video_id": video_id}

        lru_sweep(
            len(
                json.dumps(data).encode("utf-8")
            )
        )

        with open(path, "w") as file:
            mark_used(path)
            json.dump(data, file, indent=4)

def get_ytlink(source: SourceType, track_id: str):
    logger.debug(f"Attempting to read ytlink for source {source}, id {track_id}")
    if source.value == SourceType.SPOTIFY.value:
        path = CACHE_PATH / source.value / "yt-links" / f"{track_id}.json"

        if not path.exists():
            raise FileNotFoundError("Not cached yet")

        with open(path, "r") as file:
            mark_used(path)
            data = json.load(file)
            return data["video_id"]

def hash_name(string):
    name = hashlib.sha256(string.encode("utf-8")).hexdigest()
    return name