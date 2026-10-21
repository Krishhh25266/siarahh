"""Builds dist/index.html: the finished one-file site, with all images embedded.

Usage (from the repo root):  python3 scripts/build.py
Needs: Python 3 and Pillow  (pip install -r requirements.txt)
"""
import base64, io, json
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
}

html = (ROOT / "src/template.html").read_text(encoding="utf-8").replace(
    "__DATA__", json.dumps(data, ensure_ascii=False))
out = ROOT / "dist" / "index.html"
out.parent.mkdir(exist_ok=True)
out.write_text(html, encoding="utf-8")
print(f"Built {out} ({len(html) // 1024} KB)")
