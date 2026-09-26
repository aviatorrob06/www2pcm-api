import urllib.request
from pathlib import Path


APP_DIR = Path(__file__).resolve().parent.parent.parent
BIN_DIR = APP_DIR / "bin"
CONFIG_FILE = APP_DIR / "config.py"

FFMPEG_URL = "https://evermeet.cx/ffmpeg/get/zip"
FFPROBE_URL = "https://evermeet.cx/ffmpeg/get/ffprobe/zip"

YT_DLP_URL = (
    "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_macos"
)


def download(url):
    print(f"Downloading {url}")
    with urllib.request.urlopen(url) as response:
        return response.read()


def install_ffmpeg():
    # Evermeet's download API gives us the ZIP archive.
    # We use the system `unzip` command to extract it.
    import subprocess
    import tempfile
    import zipfile
    import io

    ffmpeg_zip = download(FFMPEG_URL)
    ffprobe_zip = download(FFPROBE_URL)

    with zipfile.ZipFile(io.BytesIO(ffmpeg_zip)) as archive:
        ffmpeg_name = next(
            name for name in archive.namelist()
            if name.endswith("/ffmpeg") or name == "ffmpeg"
        )

        (BIN_DIR / "ffmpeg").write_bytes(
            archive.read(ffmpeg_name)
        )

    with zipfile.ZipFile(io.BytesIO(ffprobe_zip)) as archive:
        ffprobe_name = next(
            name for name in archive.namelist()
            if name.endswith("/ffprobe") or name == "ffprobe"
        )

        (BIN_DIR / "ffprobe").write_bytes(
            archive.read(ffprobe_name)
        )

    (BIN_DIR / "ffmpeg").chmod(0o755)
    (BIN_DIR / "ffprobe").chmod(0o755)


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

    lines = config.splitlines()

    for variable, path in replacements.items():
        for i, line in enumerate(lines):
            if line.startswith(variable + " ="):
                lines[i] = f'{variable} = "{path}"'
                break
        else:
            raise RuntimeError(f"Could not find {variable} in config.py")

    CONFIG_FILE.write_text("\n".join(lines) + "\n")


def main():
    BIN_DIR.mkdir(exist_ok=True)

    install_ffmpeg()
    install_yt_dlp()
    update_config()

    print("\nInstallation complete!")


if __name__ == "__main__":
    main()