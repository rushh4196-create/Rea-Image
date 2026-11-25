#!/usr/bin/env python3
"""Strict visual, structural, and quantitative parity verifier for rea-image.

Computes aspect ratio delta, overall and per-zone 3x3 SSIM, edge-structure
correlation, color histogram similarity, perceptual CIE LAB Delta-E, normalized
RMSE, global/zone luminance bias, and automated fix directives, plus a 3-panel
side-by-side + 4x amplified difference heatmap with worst-zone boxes.
"""

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


ZONE_NAMES = [
    ["top-left", "top-center", "top-right"],
    ["mid-left", "center", "mid-right"],
    ["bottom-left", "bottom-center", "bottom-right"],
]


def rgb_to_lab(rgb: np.ndarray) -> np.ndarray:
    srgb = np.clip(rgb / 255.0, 0.0, 1.0)
    lin = np.where(srgb > 0.04045, ((srgb + 0.055) / 1.055) ** 2.4, srgb / 12.92)

    x = (lin[:, :, 0] * 0.4124564 + lin[:, :, 1] * 0.3575761 + lin[:, :, 2] * 0.1804375) / 0.95047
    y = (lin[:, :, 0] * 0.2126729 + lin[:, :, 1] * 0.7151522 + lin[:, :, 2] * 0.0721750) / 1.00000
    z = (lin[:, :, 0] * 0.0193339 + lin[:, :, 1] * 0.1191920 + lin[:, :, 2] * 0.9503041) / 1.08883

    eps = 0.008856
    kappa = 903.3
    fx = np.where(x > eps, np.cbrt(x), (kappa * x + 16.0) / 116.0)
    fy = np.where(y > eps, np.cbrt(y), (kappa * y + 16.0) / 116.0)
    fz = np.where(z > eps, np.cbrt(z), (kappa * z + 16.0) / 116.0)

    L = 116.0 * fy - 16.0
    a = 500.0 * (fx - fy)
    b = 200.0 * (fy - fz)
    return np.stack([L, a, b], axis=-1)


def compute_ssim(gray_a: np.ndarray, gray_b: np.ndarray, blocks: int = 8) -> float:
    c1 = (0.01 * 255) ** 2
    c2 = (0.03 * 255) ** 2
    h, w = gray_a.shape
    bh, bw = max(1, h // blocks), max(1, w // blocks)
    scores = []
    for i in range(blocks):
        for j in range(blocks):
            y0 = i * bh
            y1 = (i + 1) * bh if i < blocks - 1 else h
            x0 = j * bw
            x1 = (j + 1) * bw if j < blocks - 1 else w
            pa = gray_a[y0:y1, x0:x1]
            pb = gray_b[y0:y1, x0:x1]
            if pa.size == 0:
                continue
            mu_a = float(np.mean(pa))
            mu_b = float(np.mean(pb))
            var_a = float(np.var(pa))
            var_b = float(np.var(pb))
            cov = float(np.mean((pa - mu_a) * (pb - mu_b)))
            num = (2 * mu_a * mu_b + c1) * (2 * cov + c2)
            den = (mu_a**2 + mu_b**2 + c1) * (var_a + var_b + c2)
            scores.append(num / den if den > 0 else 1.0)
    return float(np.mean(scores)) if scores else 1.0


def histogram_similarity(rgb_a: np.ndarray, rgb_b: np.ndarray) -> float:
    sims = []
    for ch in range(3):
        ha, _ = np.histogram(rgb_a[:, :, ch], bins=32, range=(0, 256), density=True)
        hb, _ = np.histogram(rgb_b[:, :, ch], bins=32, range=(0, 256), density=True)
        inter = float(np.sum(np.minimum(ha, hb)) * (256 / 32))
        sims.append(inter)
    return float(np.mean(sims))


def edge_correlation(ref_rgb: Image.Image, rec_rgb: Image.Image) -> float:
    ea = np.asarray(
        ref_rgb.convert("L").filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(2)),
        dtype=np.float32,
    ).ravel()
    eb = np.asarray(
        rec_rgb.convert("L").filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(2)),
        dtype=np.float32,
    ).ravel()
    denom = float(np.linalg.norm(ea) * np.linalg.norm(eb))
    return float(np.dot(ea, eb) / denom) if denom > 1e-6 else 1.0


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify clone parity against reference image.")
    parser.add_argument("reference", help="Path to reference image")
    parser.add_argument("recreated", help="Path to recreated image")
    parser.add_argument("--out", required=True, help="Output directory for verification artifacts")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    ref_img = Image.open(args.reference).convert("RGB")
    rec_img = Image.open(args.recreated).convert("RGB")

    rw, rh = ref_img.size
    cw, ch = rec_img.size
    ref_ar = rw / max(rh, 1)
    rec_ar = cw / max(ch, 1)
    ar_delta = abs(ref_ar - rec_ar) / max(ref_ar, 1e-6)

    rec_resized = rec_img.resize((rw, rh), Image.Resampling.LANCZOS)

    arr_a = np.asarray(ref_img, dtype=np.float32)
    arr_b = np.asarray(rec_resized, dtype=np.float32)

    diff = np.abs(arr_a - arr_b)
    rmse = float(np.sqrt(np.mean((arr_a - arr_b) ** 2)))
    nrmse = rmse / 255.0

    gray_a = 0.2126 * arr_a[:, :, 0] + 0.7152 * arr_a[:, :, 1] + 0.0722 * arr_a[:, :, 2]
    gray_b = 0.2126 * arr_b[:, :, 0] + 0.7152 * arr_b[:, :, 1] + 0.0722 * arr_b[:, :, 2]
    lum_bias = float(np.mean(gray_b) - np.mean(gray_a))

    ssim = compute_ssim(gray_a, gray_b, blocks=8)
    edge_corr = edge_correlation(ref_img, rec_resized)
    hist_sim = histogram_similarity(arr_a, arr_b)

    lab_a = rgb_to_lab(arr_a)
    lab_b = rgb_to_lab(arr_b)
    delta_e_map = np.sqrt(np.sum((lab_a - lab_b) ** 2, axis=-1))
    mean_delta_e = float(np.mean(delta_e_map))

    zone_metrics = {}
    zone_list = []
    for row in range(3):
        y0 = int(row * rh / 3)
        y1 = int((row + 1) * rh / 3) if row < 2 else rh
        for col in range(3):
            x0 = int(col * rw / 3)
            x1 = int((col + 1) * rw / 3) if col < 2 else rw
            name = ZONE_NAMES[row][col]
            z_ssim = compute_ssim(gray_a[y0:y1, x0:x1], gray_b[y0:y1, x0:x1], blocks=4)
            z_de = float(np.mean(delta_e_map[y0:y1, x0:x1]))
            z_lum_bias = float(np.mean(gray_b[y0:y1, x0:x1]) - np.mean(gray_a[y0:y1, x0:x1]))
            zone_metrics[name] = {
                "ssim": round(z_ssim, 4),
                "mean_lab_delta_e": round(z_de, 2),
                "luminance_bias": round(z_lum_bias, 1),
            }
            zone_list.append((name, z_ssim, z_de, z_lum_bias, row, col))

    worst_sorted = sorted(zone_list, key=lambda item: (item[1] - item[2] / 100.0))
    worst_zones = [
        {
            "zone": z[0],
            "ssim": round(z[1], 4),
            "mean_lab_delta_e": round(z[2], 2),
            "luminance_bias": round(z[3], 1),
        }
        for z in worst_sorted[:3]
    ]
    worst_coords = {(z[4], z[5]) for z in worst_sorted[:3]}

    directives = []
    if ar_delta > 0.02:
        directives.append(f"Fix aspect ratio mismatch (delta={ar_delta:.3f})")
    if abs(lum_bias) > 10.0:
        direction = "darker" if lum_bias > 0 else "brighter"
        directives.append(
            f"Global exposure too {'bright' if lum_bias > 0 else 'dark'} by {abs(lum_bias):.1f}/255 -> shift {direction} or run calibrate_clone.py"
        )
    if mean_delta_e > 8.0 or hist_sim < 0.85:
        directives.append(
            f"Color grade drift (dE={mean_delta_e:.1f}, hist={hist_sim:.3f}) -> run calibrate_clone.py --strength 0.70"
        )
    if edge_corr < 0.75:
        directives.append(
            f"Structural edge drift (edge_corr={edge_corr:.3f}) -> refine subject position, scale, and horizon alignment"
        )
    for z in worst_zones:
        if z["mean_lab_delta_e"] > 8.0 or z["ssim"] < 0.75:
            directives.append(
                f"Refine zone '{z['zone']}' (SSIM={z['ssim']}, dE={z['mean_lab_delta_e']}, lum_bias={z['luminance_bias']:+.1f})"
            )

    diff_mag = np.mean(diff, axis=2)
    amp = np.clip(diff_mag * 4.0, 0, 255).astype(np.uint8)
    heat = np.zeros((rh, rw, 3), dtype=np.uint8)
    heat[:, :, 0] = amp
    heat[:, :, 1] = np.clip(amp * 0.35, 0, 255).astype(np.uint8)
    heat[:, :, 2] = (255 - amp) // 5
    heat_img = Image.fromarray(heat, mode="RGB")

    h_draw = ImageDraw.Draw(heat_img)
    box_w = max(2, min(rw, rh) // 250)
    for row, col in worst_coords:
        y0 = int(row * rh / 3)
        y1 = int((row + 1) * rh / 3) if row < 2 else rh
        x0 = int(col * rw / 3)
        x1 = int((col + 1) * rw / 3) if col < 2 else rw
        h_draw.rectangle([x0 + 2, y0 + 2, x1 - 2, y1 - 2], outline=(255, 255, 0), width=box_w)

    target_h = min(720, rh)
    scale = target_h / max(rh, 1)
    panel_w = max(1, int(rw * scale))

    p1 = ref_img.resize((panel_w, target_h), Image.Resampling.LANCZOS)
    p2 = rec_resized.resize((panel_w, target_h), Image.Resampling.LANCZOS)
    p3 = heat_img.resize((panel_w, target_h), Image.Resampling.LANCZOS)

    header_h = 32
    pad = 8
    comp = Image.new("RGB", (panel_w * 3 + pad * 4, target_h + header_h + pad * 2), (20, 20, 20))
    draw = ImageDraw.Draw(comp)
    labels = [
        (p1, pad, f"REFERENCE ({rw}x{rh})"),
        (p2, panel_w + pad * 2, f"RECREATED ({cw}x{ch})"),
        (p3, panel_w * 2 + pad * 3, f"DIFF x4 | SSIM={ssim:.3f} Edge={edge_corr:.2f} dE={mean_delta_e:.1f}"),
    ]
    for img_panel, x, text in labels:
        draw.text((x + 4, 8), text, fill=(240, 240, 240))
        comp.paste(img_panel, (x, header_h + pad))

    comp_path = out_dir / "comparison.png"
    comp.save(comp_path)

    metrics = {
        "reference_dimensions": [rw, rh],
        "recreated_dimensions": [cw, ch],
        "aspect_ratio_relative_delta": round(ar_delta, 4),
        "block_ssim_0_1": round(ssim, 4),
        "edge_correlation_0_1": round(edge_corr, 4),
        "color_histogram_similarity_0_1": round(hist_sim, 4),
        "mean_lab_delta_e": round(mean_delta_e, 2),
        "global_luminance_bias": round(lum_bias, 2),
        "normalized_rmse_0_1": round(nrmse, 4),
        "worst_zones": worst_zones,
        "auto_fix_directives": directives,
        "zone_metrics_3x3": zone_metrics,
        "comparison_image": str(comp_path.resolve()),
    }

    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
