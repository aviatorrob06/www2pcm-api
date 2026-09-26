import logging
import subprocess

from application.config import FFPROBE_PATH, configLogger

logger = logging.getLogger(__name__)
configLogger()


def is_valid_audio(path):
    command = [
        FFPROBE_PATH,
        "-v",
        "error",
        "-select_streams",
        "a:0",
        "-show_entries",
        "stream=codec_type",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        path
    ]

    result = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    stdout, stderr = result.communicate()

    logger.debug("stdout:", stdout.decode())
    logger.debug("stderr:", stderr.decode())
    logger.debug("return code:", result.returncode)

    if result.returncode == 0:
        return True
    else:
        return False