from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import subprocess

from app.extractor import extract_info

app = FastAPI(title="Local YouTube Downloader")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InfoRequest(BaseModel):
    url: str


class DownloadRequest(BaseModel):
    url: str
    format_id: str

@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/info")
def info(req: InfoRequest):
    """
    Step 1:
    Get metadata + available formats
    """
    result = extract_info(req.url)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result)

    return result

@app.post("/download")
def download(req: DownloadRequest):
    """
    Step 2:
    Stream selected format directly to browser
    """
    process = subprocess.Popen(
        ["yt-dlp", "-f", req.format_id, "-o", "-", req.url],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    def stream():
        while True:
            chunk = process.stdout.read(1024 * 1024)  # 1MB
            if not chunk:
                break
            yield chunk

    headers = {
        "Content-Disposition": 'attachment; filename="video.mp4"'
    }

    return StreamingResponse(
        stream(),
        media_type="video/mp4",
        headers=headers
    )