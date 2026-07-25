import code
import logging
from email import message

from fastapi import FastAPI, HTTPException
from starlette.responses import Response

from application.config import YTDLP_PATH, FFMPEG_PATH, configLogger
from application.routers import youtube
from application.services import ytdlp, ffmpeg
from application.utils import cachehelper
from application.utils.cachehelper import read_pcm, save_pcm
from application.utils.util_misc import check_executable

app = FastAPI()
logger = logging.getLogger(__name__)
configLogger()

@app.get("/")
async def root():
    return {"message": "Hello World!"}

check_executable(YTDLP_PATH)
check_executable(FFMPEG_PATH)

app.include_router(youtube.router)

