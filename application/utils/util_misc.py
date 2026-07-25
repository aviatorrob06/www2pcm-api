from pathlib import Path
from application import config
import os

def check_executable(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist. Make sure you have this binary available!")

    if not os.access(path, os.X_OK):
        raise PermissionError(
            f"{path} is not executable. This file needs to be executable for this API to work properly. Run chmod + x {path} OR setperms.sh"
        )