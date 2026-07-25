import code
import logging
from contextlib import asynccontextmanager
from email import message

from fastapi import FastAPI, HTTPException
from starlette.responses import Response
from uvicorn import lifespan

from application.config import YTDLP_PATH, FFMPEG_PATH, configLogger, CACHE_PATH
from application.routers import youtube
from application.services import ytdlp, ffmpeg
from application.utils import cachehelper
from application.utils.cachehelper import read_pcm, save_pcm
from application.utils.util_misc import check_executable

@asynccontextmanager
async def lifespan(app: FastAPI):
    (CACHE_PATH / "pcm").mkdir(parents=True, exist_ok=True)
    (CACHE_PATH / "metadata").mkdir(parents=True, exist_ok=True)

    print("Cache directories initialized")

    check_executable(YTDLP_PATH)
    check_executable(FFMPEG_PATH)


    yield

app = FastAPI(lifespan=lifespan)
logger = logging.getLogger(__name__)
configLogger()

@app.get("/")
async def root():
    return {"message": "Hello World!"}

app.include_router(youtube.router)

