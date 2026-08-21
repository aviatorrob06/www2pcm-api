# www2pcm-api
***
## Information
### What is www2pcm-api?
It is a REST-style API made in Python utilizing FastAPI with the intention of providing raw **PCM** data from select online streaming services, as well as any useful metadata about the media the audio is sourced from.

### What services are currently supported?
- YouTube ✅
- Spotify ✅
- SoundCloud ✅
- Bandcamp ❌
- Direct URLs ❌

### How does it work?
As for sourcing from YouTube, this API wraps commandline utility YT-DLP to handle the retrieving and parsing of YouTube data, and then FFMPEG is also wrapped in to format the audio properly.

### What are the audio specifications this exports?
This is customizable in the config file, but by default:
```
FFMPEG_FORMAT = "s16le"
FFMPEG_SAMPLE_RATE = "48000"
FFMPEG_AUDIO_CHANNELS = "2"
```

## Deployment
Installation script and instructions coming soon!

## API Usage
### Each service has its own endpoint:
```
- /youtube
- /spotify
- /soundcloud
```
### Each endpoint has two methods:
```
- /pcm
- /metadata
```
What the methods do are *self explanatory*.
### Each method has a corresponding argument name based on service:
```
For example:
- /soundcloud/pcm?resource_path=ARTIST/TRACK
- /youtube/metadata?video_id=VIDEO_ID_HERE
- /spotify/pcm?track_id=TRACK_ID_HERE
```
### As with any REST API...
You go to the path of the method you want. For example, to get the PCM data of a YouTube video:
```
- yourhost.com/youtube/pcm?video_id=XfELJU1mRMg
```
Or, to get the metadata of a SoundCloud track:
```
- yourhost.com/soundcloud/metadata?resource_path=fmfroma/fm-from-b-baby-im-back-1
```

### All data...
Will be returned either as a pcm file or a JSON of metadata.



## Libraries Used / Dependencies
### 1. [FastAPI](https://github.com/FastAPI/FastAPI)
Used as framework
### 2. [Uvicorn](https://github.com/Kludex/uvicorn)
Used as ASGI server
### 3. [YT-DLP](https://github.com/yt-dlp/yt-dlp)
Used for YouTube sourcing
### 4. [FFMPEG](https://ffmpeg.org/)
Used for audio data conversion/formatting
### 5. [SpotDL](https://github.com/spotDL/spotify-downloader)
Used for finding most similar YouTube video to provided Spotify track
