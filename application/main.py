import code
import logging
import tomllib
from pathlib import Path

import requests
from contextlib import asynccontextmanager
from email import message

from fastapi import FastAPI, HTTPException
from starlette.requests import Request
from starlette.responses import Response
from uvicorn import lifespan
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware

import application.config
from application.config import FFMPEG_PATH, configLogger, CACHE_PATH, DIRECT_URL_ALLOWED
from application.routers import youtube, spotify, soundcloud, bandcamp, direct
from application.services import ytdlp, ffmpeg
from application.utils import cachehelper
from application.utils.cachehelper import read_pcm, save_pcm
from application.utils.source_enum import SourceType
from application.utils.util_misc import check_executable

@asynccontextmanager
async def lifespan(app: FastAPI):
    (CACHE_PATH / SourceType.YOUTUBE.value / "metadata").mkdir(parents=True, exist_ok=True)
    (CACHE_PATH / SourceType.YOUTUBE.value / "pcm").mkdir(parents=True, exist_ok=True)
    (CACHE_PATH / SourceType.SPOTIFY.value / "yt-links").mkdir(parents=True, exist_ok=True)
    (CACHE_PATH / SourceType.SOUNDCLOUD.value / "pcm").mkdir(parents=True, exist_ok=True)
    (CACHE_PATH / SourceType.SOUNDCLOUD.value / "metadata").mkdir(parents=True, exist_ok=True)
    (CACHE_PATH / SourceType.BANDCAMP.value / "pcm").mkdir(parents=True, exist_ok=True)
    (CACHE_PATH / SourceType.BANDCAMP.value / "metadata").mkdir(parents=True, exist_ok=True)
    (CACHE_PATH / SourceType.DIRECT.value / "pcm").mkdir(parents=True, exist_ok=True)
    (CACHE_PATH / SourceType.DIRECT.value / "metadata").mkdir(parents=True, exist_ok=True)

    print("Cache directories initialized")

    check_executable(application.config.YTDLP_PATH)
    check_executable(application.config.FFMPEG_PATH)
    check_executable(application.config.FFPROBE_PATH)

    yield

app = FastAPI(lifespan=lifespan)
logger = logging.getLogger(__name__)
configLogger()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["10/minute"],
    storage_uri="redis://localhost:6379/0",
)

app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)

app.add_middleware(SlowAPIMiddleware)

@app.get("/")
async def root():
    return {"message": "www2pcm-api. Find documentation at https://github.com/aviatorrob06/www2pcm-api"}

with open(Path(__file__).resolve().parent.parent / "pyproject.toml", "rb") as f:
    config = tomllib.load(f)

@app.get("/rate-limit-test")
async def rate_limit_test(request: Request):
    return {"message": "Request successful"}

thisVersion = config["project"]["version"]
@app.get("/version")
async def getVersion():
    return thisVersion

app.include_router(youtube.router)
app.include_router(spotify.router)
app.include_router(soundcloud.router)
app.include_router(bandcamp.router)
app.include_router(direct.router)

#Check latest version
latestVersionJsonResponse = requests.get("https://raw.githubusercontent.com/aviatorrob06/www2pcm-api/refs/heads/master/LATEST_VERSION.json", timeout=10)
latestVersionJsonResponse.raise_for_status()

latestVersionJson = latestVersionJsonResponse.json()
latest_version = latestVersionJson["latest_version"]

if str(thisVersion) != str(latest_version):
    logger.warning("There is an update available!")
    logger.warning(f"Current Version: {thisVersion}")
    logger.warning(f"Latest Version: {latest_version}")

