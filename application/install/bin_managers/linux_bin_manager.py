import io
import os
import tarfile
import urllib.request
from pathlib import Path


APP_DIR = Path(__file__).resolve().parent.parent.parent
BIN_DIR = APP_DIR / "bin"
CONFIG_FILE = APP_DIR / "config.py"

FFMPEG_URL = (
    "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz"
)

YT_DLP_URL = (
    "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_linux"
)


def download(url):
    print(f"Downloading {url}")
    with urllib.request.urlopen(url) as response:
        return response.read()


def install_ffmpeg():
    archive_data = download(FFMPEG_URL)

    with tarfile.open(fileobj=io.BytesIO(archive_data), mode="r:xz") as archive:
        ffmpeg_member = next(
            member for member in archive.getmembers()
            if member.name.endswith("/bin/ffmpeg")
        )

        ffprobe_member = next(
            member for member in archive.getmembers()
            if member.name.endswith("/bin/ffprobe")
        )

        for member, destination in (
            (ffmpeg_member, BIN_DIR / "ffmpeg"),
            (ffprobe_member, BIN_DIR / "ffprobe"),
        ):
            source = archive.extractfile(member)

            if source is None:
                raise RuntimeError(f"Could not extract {member.name}")

            destination.write_bytes(source.read())
            destination.chmod(0o755)


def install_yt_dlp():
    data = download(YT_DLP_URL)

    destination = BIN_DIR / "yt-dlp"
    destination.write_bytes(data)
    destination.chmod(0o755)


def update_config():
    config = CONFIG_FILE.read_text()

    replacements = {
        "EXE_EXT": "",
    }

    for variable, path in replacements.items():
        lines = config.splitlines()

        for i, line in enumerate(lines):
            if line.startswith(variable + " ="):
                lines[i] = f'{variable} = "{path}"'
                break
        else:
            raise RuntimeError(f"Could not find {variable} in config.py")

        config = "\n".join(lines) + "\n"

    CONFIG_FILE.write_text(config)


def main():
    BIN_DIR.mkdir(exist_ok=True)

    install_ffmpeg()
    install_yt_dlp()
    update_config()

    print("\nInstallation complete!")


if __name__ == "__main__":
    main()