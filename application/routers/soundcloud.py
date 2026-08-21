import json

from fastapi import APIRouter, HTTPException
from starlette.responses import Response, JSONResponse

import application.services.spotdl
from application.config import *
import logging

from application.routers import youtube
from application.services import ytdlp
from application.services import ffmpeg
from application.utils import cachehelper
from application.utils.source_enum import SourceType

configLogger()
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/soundcloud",
    tags=["Soundcloud"]
)

@router.get("/pcm")
async def getPcm(resource_path: str):
    logger.debug(f"Attempting to get and return PCM data for soundcloud resource '{resource_path}' Checking cache first")
    try:
        cacheFile = cachehelper.read_pcm(SourceType.SOUNDCLOUD, resource_path)
        return Response(
            content=cacheFile,
            media_type="application/octet-stream"
        )
    except FileNotFoundError:
        logger.debug("Did not find PCM data for requested soundcloud source. Invoking YTDLP to cache and return PCM.")
        ytdlp_process = ytdlp.get_audio_stream(SourceType.SOUNDCLOUD, resource_path)

        pcm, ffmpeg_errors, ffmpeg_returncode = ffmpeg.convertToPcm(
            ytdlp_process.stdout
        )

        ytdlp_process.wait()

        ytdlp_errors = ytdlp_process.stderr.read()

        if ytdlp_process.returncode != 0:
            error = ytdlp_errors.decode("utf-8", errors="replace")
            raise HTTPException(
                status_code=403,
                detail={
                    "service": "yt-dlp",
                    "error": error
                }
            )

        if ffmpeg_returncode != 0:
            error = ffmpeg_errors.decode("utf-8", errors="replace")

            raise HTTPException(
                status_code=404,
                detail={
                    "service": "ffmpeg",
                    "error": error
                }
            )

        cachehelper.save_pcm(SourceType.SOUNDCLOUD, resource_path, pcm)

        return Response(
            content=pcm,
            media_type="application/octet-stream"
        )

@router.get("/metadata")
async def get_metadata(resource_path: str):
    try:
        logger.debug(f"Attempting to get metadata for {resource_path}; checking cache")
        metadata = cachehelper.read_metadata(SourceType.SOUNDCLOUD, resource_path)
        logger.debug(f"Found metadata: {metadata}")
        return metadata
    except FileNotFoundError:
        logger.debug("Did not find metadata in cache. Calling YTDLP.")
        content = ytdlp.get_metadata(SourceType.SOUNDCLOUD, resource_path)

        return JSONResponse(
            content=content
        )