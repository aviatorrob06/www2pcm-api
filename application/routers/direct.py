import json
import tempfile
from http.client import InvalidURL, HTTPResponse
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from fastapi import APIRouter, HTTPException
from starlette.responses import Response, JSONResponse

import application.services.spotdl
from application.config import *
import logging

from application.routers import youtube
from application.services import ytdlp, ffprobe
from application.services import ffmpeg
from application.utils import cachehelper, url_normalizer
from application.utils.source_enum import SourceType

configLogger()
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/direct",
    tags=["direct"]
)

@router.get("/enabled")
async def isEnabled():
    return DIRECT_URL_ALLOWED

@router.get("/pcm")
async def getPcm(url: str):
    if not application.config.DIRECT_URL_ALLOWED:
        raise HTTPException(
            status_code=403,
            detail={
                "service": "direct",
                "error": "Direct URL processing not enabled in WWW2PCM-API config!"
            }
        )
    logger.debug(f"Attempting to get and return PCM data for direct URL '{url}' Checking cache first")
    url = url_normalizer.normalize(url)
    file_name = cachehelper.hash_name(url)
    try:
        cacheFile = cachehelper.read_pcm(SourceType.DIRECT, file_name)
        return Response(
            content=cacheFile,
            media_type="application/octet-stream"
        )
    except FileNotFoundError:
        logger.debug("Did not find PCM data for requested direct URL. Sending HTTP request to it")

        try:
            response = urlopen(url)

            contentType = response.headers.get("Content-Type")

            if (contentType and contentType.startswith("audio/")) or (
                    contentType and contentType == "application/octet-stream"):
                logger.debug("This is an audio file content type!: " + contentType)
                logger.debug("Downloading temp file")

                with tempfile.NamedTemporaryFile() as temp:
                    with open(temp.name, "wb") as file:
                        while chunk := response.read(8192):
                            file.write(chunk)

                        temp.flush()

                        logger.debug("Downloaded as temporary file: " + temp.name)
                        logger.debug("Prompting FFProbe to probe audio file for validity")
                        if ffprobe.is_valid_audio(temp.name):
                            logger.debug(
                                "FFProbe recognizes this file! Passing temporary file to FFmpeg to process into PCM")
                            pcm_data, errors, returncode = ffmpeg.convertToPcm(
                                open(temp.name)
                            )
                            if returncode == 0:
                                logger.debug(
                                    "PCM data successfully output. Hashing URL into file name, then saving to cache")
                                fileName = cachehelper.hash_name(url)
                                cachehelper.save_pcm(SourceType.DIRECT, fileName, pcm_data)
                                return Response(
                                    content=pcm_data,
                                    media_type="application/octet-stream"
                                )
                        else:
                            raise HTTPException(
                                status_code=403,
                                detail={
                                    "service": "direct",
                                    "error": "Invalid audio format per FFProbe!"
                                }
                            )
            else:
                raise HTTPException(
                    status_code=403,
                    detail={
                        "service": "direct",
                        "error": "Invalid Content-Type. Is this an audio?"
                    }
                )

        except HTTPError as e:
            raise HTTPException(
                status_code=404,
                detail={
                    "service": "direct",
                    "error": "HTTP Error: " + str(e.code)
                }
            )
        except URLError as e:
            raise HTTPException(
                status_code=403,
                detail={
                    "service": "direct",
                    "error": "URL Error: " + str(e.reason)
                }
            )
        except InvalidURL as e:
            raise HTTPException(
                status_code=403,
                detail={
                    "service": "direct",
                    "error": str(e)
                }
            )
