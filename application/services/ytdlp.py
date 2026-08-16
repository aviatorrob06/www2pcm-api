from application.config import *
import subprocess
import json
import logging
from application.config import YTDLP_PATH
from application.utils.source_enum import SourceType
from application.utils.cachehelper import read_metadata, save_metadata

configLogger()
logger = logging.getLogger(__name__)

def get_metadata(video_id):
    logger.debug(f"Attempting to get metadata for {video_id}; checking cache")

    try:
        metadata = read_metadata(video_id)
        logger.debug(f"Found metadata: {metadata}")
        return metadata
    except:
        logger.debug("No metadata cached. Calling YT-DLP.")
        command = [
            YTDLP_PATH,
            "--dump-json",
            "https://www.youtube.com/watch?v=" + video_id,
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )

        if (result.returncode != 0):
            raise Exception(result.stderr)

        logger.debug("Subprocess success. Parsing results")
        data = json.loads(result.stdout)

        save_metadata(SourceType.YOUTUBE, video_id, data)

        return data


def get_audio_stream(video_id: str):
    logger.debug("Audio requested. Running YT-DLP.")
    command = [
        YTDLP_PATH,
        "-f", "bestaudio",
        "-o",
        "-",
        f"https://www.youtube.com/watch?v={video_id}"
    ]

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    logger.debug("Process finished. Returning subprocess instance")

    return process

