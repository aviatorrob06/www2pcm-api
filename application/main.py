import code
import logging
from contextlib import asynccontextmanager
from email import message

from fastapi import FastAPI, HTTPException
from starlette.responses import Response
from uvicorn import lifespan

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

@app.get("/")
async def root():
    return {"message": "www2pcm-api. Find documentation at https://github.com/aviatorrob06/www2pcm-api"}

app.include_router(youtube.router)
app.include_router(spotify.router)
app.include_router(soundcloud.router)
app.include_router(bandcamp.router)
app.include_router(direct.router)

