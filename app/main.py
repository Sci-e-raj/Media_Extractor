from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.extractor import extract_info
from fastapi.responses import StreamingResponse
import subprocess

app = FastAPI(title="Local Media Extractor")

class InfoRequest(BaseModel):
    url: str

@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/info")
def info(req: InfoRequest):
    result = extract_info(req.url)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result)

    return result

@app.post("/download")
def download(req: dict):
    url = req.get("url")
    format_id = req.get("format_id")

    if not url or not format_id:
        raise HTTPException(status_code=400, detail="url and format_id required")

    process = subprocess.Popen(
        ["yt-dlp", "-f", format_id, "-o", "-", url],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    def stream():
        while True:
            chunk = process.stdout.read(1024 * 1024)  # 1MB chunks
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