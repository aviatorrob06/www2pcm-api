import json

from fastapi import APIRouter, HTTPException
from starlette.responses import Response

import application.services.spotdl
from application.config import *
import logging

from application.routers import youtube
from application.utils import cachehelper
from application.utils.cachehelper import mark_used
from application.utils.source_enum import SourceType

configLogger()
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/spotify",
    tags=["Spotify"]
)

@router.get("/pcm")
async def get_spotify_pcm(track_id: str):
        logger.debug(f"Attempting to get and return PCM data for {track_id}. Checking ytlink cache")
        try:
            video_id = cachehelper.get_ytlink(SourceType.SPOTIFY, track_id)
            try:
                pcm = cachehelper.read_pcm(SourceType.YOUTUBE, video_id)
                return Response(
                    content=pcm,
                    media_type="application/octet-stream"
                )
            except FileNotFoundError:
                logger.debug("Did NOT find cached PCM data. Calling YouTube PCM endpoint.")
                return await youtube.get_pcm(video_id)
        except FileNotFoundError:
            logger.debug("Did not find ytlink cache, running SpotDL")
            try:
                video_id = application.services.spotdl.get_yt_id(track_id)
                cachehelper.save_ytlink(SourceType.SPOTIFY, track_id, video_id)
                logger.debug("Successfully got and saved ytlink. Calling YouTube PCM endpoint.")
                return await youtube.get_pcm(video_id)
            except RuntimeError as e:
                raise HTTPException(
                    status_code=403,
                    detail={
                        "service": "SpotDL",
                        "error": str(e)
                    }
                )



