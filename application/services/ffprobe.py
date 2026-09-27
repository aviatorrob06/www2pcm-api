import json
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

def probe_metadata(filename):
    result = subprocess.run(
        [
            FFPROBE_PATH,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            filename,
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    data = json.loads(result.stdout)

    format_data = data.get("format", {})
    tags = format_data.get("tags", {})

    metadata = {
        key: value
        for key, value in {
            "title": tags.get("title"),
            "artist": tags.get("artist"),
            "album": tags.get("album"),
            "album_artist": tags.get("album_artist"),
            "genre": tags.get("genre"),
            "date": tags.get("date"),
            "track": tags.get("track"),
            "disc": tags.get("disc"),
            "duration": format_data.get("duration"),
            "format": format_data.get("format_name"),
            "bitrate": format_data.get("bit_rate"),
        }.items()
        if value is not None
    }


    return metadata