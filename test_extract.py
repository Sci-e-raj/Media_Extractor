import subprocess
import json

url = input("Enter video URL: ")

result = subprocess.run(
    ["yt-dlp", "-J", url],
    capture_output=True,
    text=True
)

print("Return code:", result.returncode)

if result.returncode == 0:
    data = json.loads(result.stdout)
    print("Title:", data.get("title"))
    print("Duration (seconds):", data.get("duration"))
else:
    print("Error:", result.stderr)
