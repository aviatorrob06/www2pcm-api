import logging
import subprocess

from application import config
from application.config import configLogger

logger = logging.getLogger(__name__)
configLogger()

def convertToPcm(input):
    logger.debug("Attempting to convert YTDLP input into PCM")
    command = [
        config.FFMPEG_PATH,
        "-i",
        "pipe:0",
        "-ar",
        config.FFMPEG_SAMPLE_RATE,
        "-ac",
        config.FFMPEG_AUDIO_CHANNELS,
        "-f",
        config.FFMPEG_FORMAT,
        "pipe:1"
    ]

    process = subprocess.Popen(
        command,
        stdin=input,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    pcm_data, errors = process.communicate()

    logger.debug("Returning PCM data, errors, and return code")

    return pcm_data, errors, process.returncode