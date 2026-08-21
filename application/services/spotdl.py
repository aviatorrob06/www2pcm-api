import subprocess

from application.config import *
import logging
from urllib.parse import urlparse, parse_qs

configLogger()
logger = logging.getLogger(__name__)


def get_yt_id(id: str):
    logger.debug(f"Attempting to match Spotify ID {id} to YouTube URL")
    result = subprocess.run(
        [
            "spotdl",
            "url",
            f"https://open.spotify.com/track/{id}",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    logger.debug(f"spotDL stdout: {result.stdout}")
    logger.debug(f"spotDL stderr: {result.stderr}")
    logger.debug(f"spotDL return code: {result.returncode}")

    if result.returncode != 0:
        raise RuntimeError(
            f"spotDL failed with exit code {result.returncode}: " 
            f"{result.stderr.strip()}"
        )

    output = result.stdout.strip()

    youtube_url = next(
        (
            line.strip()
            for line in output.splitlines()
            if urlparse(line.strip()).scheme in ("http", "https")
        ),
        None
    )

    if youtube_url is None:
        raise RuntimeError("spotDL did not return a URL")

    return parse_qs(urlparse(youtube_url).query)["v"][0]