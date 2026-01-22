import subprocess
import json


def extract_info(url: str):
    """
    Uses yt-dlp to extract metadata only.
    No downloading.
    """
    try:
        result = subprocess.run(
            ["yt-dlp", "-J", url],
            capture_output=True,
            text=True,
            check=True
        )

        data = json.loads(result.stdout)

        return {
            "title": data.get("title"),
            "duration": data.get("duration"),
            "formats": simplify_formats(data.get("formats", []))
        }

    except subprocess.CalledProcessError as e:
        return {
            "error": "yt-dlp failed",
            "details": e.stderr
        }


def simplify_formats(formats):
    simplified = []

    for f in formats:
        if f.get("filesize") and f.get("vcodec") != "none":
            simplified.append({
                "format_id": f.get("format_id"),
                "ext": f.get("ext"),
                "resolution": f.get("resolution"),
                "filesize_mb": round(f["filesize"] / (1024 * 1024), 2),
                "vcodec": f.get("vcodec"),
                "acodec": f.get("acodec"),
            })

    return simplified
