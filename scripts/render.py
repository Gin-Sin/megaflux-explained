"""Render all site videos and extract stable final-frame posters."""
from pathlib import Path
import subprocess
import sys
import argparse
import json

ROOT = Path(__file__).resolve().parents[1]
SCENES = {"RoutingSkew": "routing-skew", "ForwardPipeline": "forward-pipeline", "BackwardReduction": "backward-reduction"}
parser = argparse.ArgumentParser()
parser.add_argument("--draft", action="store_true", help="Render review copies without replacing site assets")
parser.add_argument("--only", choices=list(SCENES), help="Render just one scene")
args = parser.parse_args()
assets = ROOT / ("media/preview" if args.draft else "site/assets")
assets.mkdir(parents=True, exist_ok=True)
for scene, slug in SCENES.items():
    if args.only and scene != args.only:
        continue
    subprocess.run([sys.executable, "-m", "manim", "render", "-ql" if args.draft else "-qh", "--fps", "15" if args.draft else "30",
                    "--disable_caching", "--media_dir", str(ROOT / "media"),
                    str(ROOT / "animations/scenes.py"), scene], cwd=ROOT, check=True)
    candidates = list((ROOT / "media/videos").rglob(f"{scene}.mp4"))
    src = max(candidates, key=lambda p: p.stat().st_mtime)
    dest = assets / f"{slug}.mp4"
    subprocess.run(["ffmpeg", "-y", "-i", str(src), "-c", "copy", "-movflags", "+faststart", str(dest)], check=True, capture_output=True)
    subprocess.run(["ffmpeg", "-y", "-sseof", "-0.5", "-i", str(dest), "-frames:v", "1", "-update", "1", str(assets / f"{slug}.png")], check=True, capture_output=True)
    print(f"Rendered {dest.relative_to(ROOT)}", flush=True)
if not args.draft:
    manifest = [json.loads((ROOT / "media/audit" / f"{scene}.json").read_text()) for scene in SCENES]
    (assets / "animation-audit.json").write_text(json.dumps(manifest, indent=2))
