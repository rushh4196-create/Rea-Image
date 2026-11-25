#!/usr/bin/env python3
"""Deep deterministic forensic image inspector for rea-image.

Extracts dimensions, nearest aspect ratio, EXIF/PNG/XMP/AIGC metadata, global
12-color hex palette, 9-zone (3x3) spatial color/luminance/saturation map,
tone-curve percentiles, directional lighting balance, sharpness/grain index,
edge density, flat-region ratio, a 6x6 coordinate grid overlay, and a 3x3
high-res tile sheet.
"""

import argparse
import json
import math
import os
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import ExifTags, Image, ImageDraw, ImageFilter


SUPPORTED_ASPECT_RATIOS = [
    ("1:1", 1.0),
    ("4:5", 4 / 5),
    ("5:4", 5 / 4),
    ("3:4", 3 / 4),
    ("4:3", 4 / 3),
    ("2:3", 2 / 3),
    ("3:2", 3 / 2),
    ("9:16", 9 / 16),
    ("16:9", 16 / 9),
    ("21:9", 21 / 9),
]

AIGC_KEYWORDS = (
    "midjourney",
    "dall-e",
    "dalle",
    "stable diffusion",
    "comfyui",
    "automatic1111",
    "invokeai",
    "novelai",
    "firefly",
    "imagen",
    "flux",
    "c2pa",
    "aigc",
    "ai generated",
    "trainedalgorithmicmedia",
    "parameters",
    "prompt",
    "cfg scale",
    "steps:",
)

ZONE_NAMES = [
    ["top-left", "top-center", "top-right"],
    ["mid-left", "center", "mid-right"],
    ["bottom-left", "bottom-center", "bottom-right"],
]


def nearest_aspect_ratio(width: int, height: int) -> dict:
    ratio = width / max(height, 1)
    best_label, best_val = min(
        SUPPORTED_ASPECT_RATIOS, key=lambda item: abs(item[1] - ratio)
    )
    gcd = math.gcd(width, height)
    return {
        "exact_ratio": f"{width // gcd}:{height // gcd}",
        "decimal": round(ratio, 4),
        "nearest_standard": best_label,
        "nearest_standard_decimal": round(best_val, 4),
    }


def extract_metadata(img: Image.Image) -> dict:
    meta = {
        "format": img.format,
        "mode": img.mode,
        "exif": {},
        "info_keys": sorted(list(img.info.keys())),
        "aigc_signals": [],
        "camera_signals": [],
    }

    try:
        exif_raw = img.getexif()
        if exif_raw:
            for tag_id, val in exif_raw.items():
                tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                val_str = str(val)
                if len(val_str) > 300:
                    val_str = val_str[:300] + "...[truncated]"
                meta["exif"][tag_name] = val_str
                if tag_name in (
                    "Make",
                    "Model",
                    "LensModel",
                    "ExposureTime",
                    "FNumber",
                    "ISOSpeedRatings",
                    "FocalLength",
                ):
                    meta["camera_signals"].append(f"{tag_name}={val_str}")
    except Exception:
        pass

    blob_parts = [f"{k}:{v}" for k, v in meta["exif"].items()]
    for k, v in img.info.items():
        if isinstance(v, bytes):
            try:
                text = v.decode("utf-8", errors="ignore")
            except Exception:
                text = ""
        else:
            text = str(v)
        if text:
            blob_parts.append(f"{k}:{text[:2000]}")
    combined = "\n".join(blob_parts).lower()

    for kw in AIGC_KEYWORDS:
        if kw in combined:
            meta["aigc_signals"].append(kw)

    return meta


def extract_palette(rgb_img: Image.Image, num_colors: int = 12) -> list:
    small = rgb_img.copy()
    small.thumbnail((256, 256))
    quant = small.quantize(colors=num_colors, method=Image.Quantize.MEDIANCUT)
    palette = quant.getpalette()
    counts = Counter(quant.getdata())
    total = sum(counts.values()) or 1

    colors = []
    for idx, count in counts.most_common(num_colors):
        r, g, b = palette[idx * 3 : idx * 3 + 3]
        colors.append(
            {
                "hex": f"#{r:02X}{g:02X}{b:02X}",
                "rgb": [int(r), int(g), int(b)],
                "percent": round(100.0 * count / total, 2),
            }
        )
    return colors


def extract_spatial_zones(rgb_img: Image.Image) -> dict:
    w, h = rgb_img.size
    zones = {}
    for row in range(3):
        y0 = int(row * h / 3)
        y1 = int((row + 1) * h / 3) if row < 2 else h
        for col in range(3):
            x0 = int(col * w / 3)
            x1 = int((col + 1) * w / 3) if col < 2 else w
            crop = rgb_img.crop((x0, y0, x1, y1))
            arr = np.asarray(crop, dtype=np.float32)
            lum = 0.2126 * arr[:, :, 0] + 0.7152 * arr[:, :, 1] + 0.0722 * arr[:, :, 2]
            hsv = np.asarray(crop.convert("HSV"), dtype=np.float32)
            top_colors = extract_palette(crop, num_colors=3)
            zones[ZONE_NAMES[row][col]] = {
                "bbox_px": [x0, y0, x1, y1],
                "mean_luminance": round(float(np.mean(lum)), 1),
                "mean_saturation": round(float(np.mean(hsv[:, :, 1])) / 255.0, 3),
                "top_hex": [c["hex"] for c in top_colors],
            }
    return zones


def compute_visual_metrics(rgb_img: Image.Image) -> dict:
    arr = np.asarray(rgb_img, dtype=np.float32)
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]

    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    mean_lum = float(np.mean(lum))
    std_lum = float(np.std(lum))

    p02, p15, p50, p85, p98 = [
        round(float(x), 1) for x in np.percentile(lum, [2, 15, 50, 85, 98])
    ]

    hsv_arr = np.asarray(rgb_img.convert("HSV"), dtype=np.float32)
    mean_sat = float(np.mean(hsv_arr[:, :, 1])) / 255.0

    warmth = float(np.mean(r - b))
    temp_label = "warm" if warmth > 12 else ("cool" if warmth < -12 else "neutral")

    h, w = lum.shape
    left_lum = float(np.mean(lum[:, : w // 2]))
    right_lum = float(np.mean(lum[:, w // 2 :]))
    top_lum = float(np.mean(lum[: h // 2, :]))
    bottom_lum = float(np.mean(lum[h // 2 :, :]))

    lr_diff = left_lum - right_lum
    tb_diff = top_lum - bottom_lum
    horiz_light = (
        "balanced"
        if abs(lr_diff) < 8
        else ("brighter_left" if lr_diff > 0 else "brighter_right")
    )
    vert_light = (
        "balanced"
        if abs(tb_diff) < 8
        else ("brighter_top" if tb_diff > 0 else "brighter_bottom")
    )

    gray = rgb_img.convert("L")
    edges = gray.filter(ImageFilter.FIND_EDGES)
    edge_arr = np.asarray(edges, dtype=np.float32)
    edge_density = float(np.mean(edge_arr > 30))
    flat_ratio = float(np.mean(edge_arr < 5))

    g_arr = np.asarray(gray, dtype=np.float32)
    if g_arr.shape[0] > 2 and g_arr.shape[1] > 2:
        lap = (
            -4 * g_arr[1:-1, 1:-1]
            + g_arr[:-2, 1:-1]
            + g_arr[2:, 1:-1]
            + g_arr[1:-1, :-2]
            + g_arr[1:-1, 2:]
        )
        sharpness_var = float(np.var(lap))
    else:
        sharpness_var = 0.0

    return {
        "mean_luminance_0_255": round(mean_lum, 2),
        "contrast_std": round(std_lum, 2),
        "tone_curve_percentiles": {
            "p02_black": p02,
            "p15_shadows": p15,
            "p50_midtones": p50,
            "p85_highlights": p85,
            "p98_white": p98,
        },
        "mean_saturation_0_1": round(mean_sat, 3),
        "color_temperature": {"label": temp_label, "r_minus_b": round(warmth, 2)},
        "lighting_balance": {
            "horizontal": horiz_light,
            "left_minus_right": round(lr_diff, 2),
            "vertical": vert_light,
            "top_minus_bottom": round(tb_diff, 2),
        },
        "sharpness_laplacian_var": round(sharpness_var, 2),
        "edge_density_0_1": round(edge_density, 4),
        "flat_region_ratio_0_1": round(flat_ratio, 4),
    }


def save_grid_overlay(rgb_img: Image.Image, out_path: Path) -> None:
    canvas = rgb_img.copy()
    draw = ImageDraw.Draw(canvas)
    w, h = canvas.size
    major_w = max(2, min(w, h) // 350)
    minor_w = max(1, min(w, h) // 600)

    for i in range(1, 6):
        frac = i / 6.0
        x = int(w * frac)
        y = int(h * frac)
        if i == 3:
            color, lw = (255, 0, 255), major_w
        elif i in (2, 4):
            color, lw = (0, 255, 255), major_w
        else:
            color, lw = (255, 200, 0), minor_w

        draw.line([(x, 0), (x, h)], fill=color, width=lw)
        draw.line([(0, y), (w, y)], fill=color, width=lw)
        draw.text((x + 3, 4), f"{int(frac*100)}%({x})", fill=(255, 255, 0))
        draw.text((4, y + 3), f"{int(frac*100)}%({y})", fill=(255, 255, 0))

    canvas.save(out_path)


def save_tiles_3x3(rgb_img: Image.Image, out_path: Path) -> None:
    w, h = rgb_img.size
    pad = 8
    sheet = Image.new("RGB", (w + pad * 4, h + pad * 4), (20, 20, 20))
    draw = ImageDraw.Draw(sheet)

    for row in range(3):
        y0 = int(row * h / 3)
        y1 = int((row + 1) * h / 3) if row < 2 else h
        for col in range(3):
            x0 = int(col * w / 3)
            x1 = int((col + 1) * w / 3) if col < 2 else w
            crop = rgb_img.crop((x0, y0, x1, y1))
            px = x0 + pad * (col + 1)
            py = y0 + pad * (row + 1)
            sheet.paste(crop, (px, py))
            label = ZONE_NAMES[row][col]
            draw.rectangle([px, py, px + len(label) * 7 + 8, py + 16], fill=(0, 0, 0))
            draw.text((px + 4, py + 2), label, fill=(255, 255, 0))

    sheet.save(out_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Deep forensic image inspector for rea-image.")
    parser.add_argument("image", help="Path to reference image")
    parser.add_argument("--out", required=True, help="Output directory for forensic artifacts")
    args = parser.parse_args()

    src = Path(args.image)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    with Image.open(src) as img:
        w, h = img.size
        metadata = extract_metadata(img)
        rgb = img.convert("RGB")
        palette = extract_palette(rgb, num_colors=12)
        spatial_zones = extract_spatial_zones(rgb)
        metrics = compute_visual_metrics(rgb)

        save_grid_overlay(rgb, out_dir / "grid_overlay.png")
        save_tiles_3x3(rgb, out_dir / "tiles_3x3.png")

    report = {
        "file": str(src.resolve()),
        "file_size_bytes": os.path.getsize(src),
        "dimensions": {"width": w, "height": h},
        "aspect_ratio": nearest_aspect_ratio(w, h),
        "metadata": metadata,
        "palette": palette,
        "spatial_zones_3x3": spatial_zones,
        "visual_metrics": metrics,
        "artifacts": {
            "grid_overlay": str((out_dir / "grid_overlay.png").resolve()),
            "tiles_3x3": str((out_dir / "tiles_3x3.png").resolve()),
        },
    }

    report_path = out_dir / "report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
