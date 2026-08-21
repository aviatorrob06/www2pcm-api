from application.config import *
import subprocess
import json
import logging
from application.config import YTDLP_PATH
from application.utils.source_enum import SourceType
from application.utils.cachehelper import read_metadata, save_metadata

configLogger()
logger = logging.getLogger(__name__)

def get_metadata(sourceType: SourceType, video_id:str):
    urlbase = ""
    match sourceType:
        case SourceType.YOUTUBE:
            urlbase = "https://www.youtube.com/watch?v="
        case SourceType.SOUNDCLOUD:
            urlbase = "https://soundcloud.com/"
    command = [
        YTDLP_PATH,
        "--dump-json",
        urlbase + video_id,
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

    save_metadata(sourceType, video_id, data)

    return data


def get_audio_stream(sourceType: SourceType, video_id: str):
    logger.debug("Audio requested. Running YT-DLP.")
    urlbase = ""
    match sourceType:
        case SourceType.YOUTUBE:
            urlbase = "https://www.youtube.com/watch?v="
        case SourceType.SOUNDCLOUD:
            urlbase = "https://soundcloud.com/"
    command = [
        YTDLP_PATH,
        "-f", "bestaudio",
        "-o",
        "-",
        f"{urlbase}{video_id}"
    ]

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    logger.debug("Process finished. Returning subprocess instance")

    return process

