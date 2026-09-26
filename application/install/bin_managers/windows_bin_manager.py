import io
import zipfile
import urllib.request
from pathlib import Path


APP_DIR = Path(__file__).resolve().parent.parent.parent
BIN_DIR = APP_DIR / "bin"
CONFIG_FILE = APP_DIR / "config.py"

FFMPEG_URL = (
    "https://github.com/BtbN/FFmpeg-Builds/releases/latest/"
    "download/latest/ffmpeg-master-latest-win64-gpl.zip"
)

YT_DLP_URL = (
    "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
)


def download(url):
    print(f"Downloading {url}")
    with urllib.request.urlopen(url) as response:
        return response.read()


def install_ffmpeg():
    archive_data = download(FFMPEG_URL)

    with zipfile.ZipFile(io.BytesIO(archive_data)) as archive:
        ffmpeg_name = next(
            name for name in archive.namelist()
            if name.endswith("/bin/ffmpeg.exe")
        )

        ffprobe_name = next(
            name for name in archive.namelist()
            if name.endswith("/bin/ffprobe.exe")
        )

        (BIN_DIR / "ffmpeg.exe").write_bytes(
            archive.read(ffmpeg_name)
        )

        (BIN_DIR / "ffprobe.exe").write_bytes(
            archive.read(ffprobe_name)
        )


def install_yt_dlp():
    data = download(YT_DLP_URL)
    (BIN_DIR / "yt-dlp.exe").write_bytes(data)


def update_config():
    config = CONFIG_FILE.read_text()

    replacements = {
        "EXE_EXT": ".exe",
    }

    lines = config.splitlines()

    for variable, path in replacements.items():
        for i, line in enumerate(lines):
            if line.startswith(variable + " ="):
                lines[i] = f'{variable} = r"{path}"'
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