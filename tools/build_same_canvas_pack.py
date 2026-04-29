#!/usr/bin/env python3
from pathlib import Path
import json
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "data" / "same-canvas-coordinate-map.json"
OUT_DIR = ROOT / "assets" / "avatar" / "live2d" / "final" / "layers_png_same_canvas"

def main():
    config = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    canvas_w, canvas_h = config.get("canvas_size", [4096, 4096])
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for output_name, layer in config["layers"].items():
        src = ROOT / layer["source"]
        if not src.exists():
            print(f"[missing] {src}")
            continue

        img = Image.open(src).convert("RGBA")
        scale = float(layer.get("scale", 1.0))
        if scale != 1.0:
            img = img.resize(
                (max(1, int(img.width * scale)), max(1, int(img.height * scale))),
                Image.LANCZOS,
            )

        canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        canvas.alpha_composite(img, (int(layer.get("x", 0)), int(layer.get("y", 0))))
        canvas.save(OUT_DIR / output_name)
        print(f"[ok] {output_name}")

    (OUT_DIR / "README.md").write_text(
        "# Same Canvas Layer Pack\n\n"
        "Generated from `data/same-canvas-coordinate-map.json`. "
        "These 4096x4096 transparent PNGs require visual review before PSD assembly.\n",
        encoding="utf-8",
    )

if __name__ == "__main__":
    main()
