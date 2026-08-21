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
