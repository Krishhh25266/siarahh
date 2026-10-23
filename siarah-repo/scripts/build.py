"""Builds dist/index.html and copies optional homepage media into dist/.

Usage (from the repo root):  python3 scripts/build.py
Needs: Python 3 and Pillow  (pip install -r requirements.txt)
"""
import base64, io, json, shutil
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent

def uri(path, width, quality):
    im = Image.open(path).convert("RGB")
    im = im.resize((width, int(im.height * width / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

designs = json.loads((ROOT / "data/designs.json").read_text(encoding="utf-8"))["designs"]
prints = json.loads((ROOT / "data/prints.json").read_text(encoding="utf-8"))["prints"]

home_media_source = ROOT / "assets" / "homepage"
home_media_output = ROOT / "dist" / "homepage-media"
if home_media_output.exists():
    shutil.rmtree(home_media_output)
home_media = {}
media_files = {
    "video": ("campaign", (".mp4", ".webm")),
    "photo": ("campaign-photo", (".jpg", ".jpeg", ".png", ".webp")),
}
for media_key, (media_stem, suffixes) in media_files.items():
    media_file = next(
        (home_media_source / f"{media_stem}{suffix}" for suffix in suffixes
         if (home_media_source / f"{media_stem}{suffix}").is_file()),
        None,
    )
    if media_file:
        home_media_output.mkdir(parents=True, exist_ok=True)
        shutil.copy2(media_file, home_media_output / media_file.name)
        home_media[media_key] = f"homepage-media/{media_file.name}"

data = {
    "designs": [
        {"id": d["id"], "name": d["name"], "tagline": d["tagline"],
         "main": uri(ROOT / d["images"]["main"], 420, 78),
         "det": uri(ROOT / d["images"]["details"], 420, 78)}
        for d in designs
    ],
    "prints": [
        {"id": p["id"], "name": p["name"], "tagline": p["tagline"],
         "img": uri(ROOT / p["images"]["swatch"], 150, 80)}
        for p in prints
    ],
    "homeMedia": home_media,
}

html = (ROOT / "src/template.html").read_text(encoding="utf-8").replace(
    "__DATA__", json.dumps(data, ensure_ascii=False))
out = ROOT / "dist" / "index.html"
out.parent.mkdir(exist_ok=True)
out.write_text(html, encoding="utf-8")
print(f"Built {out} ({len(html) // 1024} KB)")
