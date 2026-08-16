import logging

from fastapi import APIRouter, HTTPException, Response
from starlette.responses import JSONResponse

from application.config import configLogger
from application.services import ffmpeg, ytdlp
from application.utils import cachehelper
from application.utils.cachehelper import save_pcm
from application.utils.source_enum import SourceType

configLogger()
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/youtube",
    tags=["YouTube"]
)

@router.get("/pcm")
async def get_pcm(video_id: str):
    try:
        logger.debug(f"Attempting to get and return PCM data for {video_id}. Checking cache")
        pcm = cachehelper.read_pcm(SourceType.YOUTUBE, video_id)
        return Response(
            content=pcm,
            media_type="application/octet-stream"
        )
    except FileNotFoundError:
        logger.debug("Did not find in cache. Requesting audio stream from YT-DLP, then feeding into FFMPEG.")
        ytdlp_process = ytdlp.get_audio_stream(video_id)

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

        save_pcm(SourceType.YOUTUBE, video_id, pcm)

        return Response(
            content=pcm,
            media_type="application/octet-stream"
        )

@router.get("/metadata")
async def get_metadata(video_id: str):
    content = ytdlp.get_metadata(SourceType.YOUTUBE, video_id)

    return JSONResponse(
        content=content
    )
