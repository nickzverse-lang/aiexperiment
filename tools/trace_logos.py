"""Trace the BLUORNG logo PNGs into SVG paths (needs: pip install potracer pillow numpy).

Run: python3 tools/trace_logos.py <dir with 1.png..5.png>
"""
import pathlib
import sys

import numpy as np
import potrace
from PIL import Image

OUT = pathlib.Path(__file__).resolve().parent / "book" / "brand"
# name: (file, how to pick the ink pixels)
LOGOS = {
    "monogram": ("1.png", "alpha"),
    "mark": ("3.png", "dark"),
    "wordmark": ("4.png", "light"),
    "script": ("5.png", "light"),
}


def ink(img, mode):
    if mode == "alpha":
        return np.array(img.convert("RGBA"))[:, :, 3] > 128
    g = np.array(img.convert("L"))
    return g < 128 if mode == "dark" else g > 128


def trace(mask):
    ys, xs = np.nonzero(mask)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    mask = mask[y0:y1, x0:x1]
    plist = potrace.Bitmap(~mask).trace(turdsize=4, alphamax=1.0, opticurve=True, opttolerance=0.2)
    f = lambda p: f"{p.x:.1f} {p.y:.1f}"
    parts = []
    for curve in plist:
        d = [f"M{f(curve.start_point)}"]
        for s in curve.segments:
            if s.is_corner:
                d.append(f"L{f(s.c)}L{f(s.end_point)}")
            else:
                d.append(f"C{f(s.c1)} {f(s.c2)} {f(s.end_point)}")
        parts.append("".join(d) + "Z")
    return x1 - x0, y1 - y0, "".join(parts)


def main(src):
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (file, mode) in LOGOS.items():
        w, h, d = trace(ink(Image.open(pathlib.Path(src) / file), mode))
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}"><path fill-rule="evenodd" d="{d}"/></svg>'
        (OUT / f"{name}.svg").write_text(svg)
        print(name, w, h, len(svg))


if __name__ == "__main__":
    main(sys.argv[1])
