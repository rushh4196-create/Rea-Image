#!/usr/bin/env python3
"""Post-generation dimension and LAB color-grade calibrator for rea-image.

Matches the recreated image's exact pixel resolution to the reference and
transfers the reference's Reinhard LAB luminance/color distribution at a
controllable blend strength (0.0 = resize only, 1.0 = full LAB match).
"""

import argparse
from pathlib import Path

import numpy as np
from PIL import Image


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


def lab_to_rgb(lab: np.ndarray) -> np.ndarray:
    L, a, b = lab[:, :, 0], lab[:, :, 1], lab[:, :, 2]
    fy = (L + 16.0) / 116.0
    fx = a / 500.0 + fy
    fz = fy - b / 200.0

    eps = 0.008856
    kappa = 903.3
    x = np.where(fx**3 > eps, fx**3, (116.0 * fx - 16.0) / kappa) * 0.95047
    y = np.where(L > kappa * eps, ((L + 16.0) / 116.0) ** 3, L / kappa) * 1.00000
    z = np.where(fz**3 > eps, fz**3, (116.0 * fz - 16.0) / kappa) * 1.08883

    r_lin = x * 3.2404542 - y * 1.5371385 - z * 0.4985314
    g_lin = -x * 0.9692660 + y * 1.8760108 + z * 0.0415560
    b_lin = x * 0.0556434 - y * 0.2040259 + z * 1.0572252

    lin = np.stack([r_lin, g_lin, b_lin], axis=-1)
    lin = np.clip(lin, 0.0, 1.0)
    srgb = np.where(lin > 0.0031308, 1.055 * (lin ** (1.0 / 2.4)) - 0.055, 12.92 * lin)
    return np.clip(srgb * 255.0, 0.0, 255.0).astype(np.uint8)


def main() -> None:
    parser = argparse.ArgumentParser(description="Calibrate recreated image resolution and LAB color grade.")
    parser.add_argument("reference", help="Path to reference image")
    parser.add_argument("recreated", help="Path to recreated image")
    parser.add_argument("--out", required=True, help="Output path for calibrated image")
    parser.add_argument(
        "--strength",
        type=float,
        default=0.70,
        help="LAB color-grade transfer strength from 0.0 (resize only) to 1.0 (full match)",
    )
    args = parser.parse_args()

    ref = Image.open(args.reference).convert("RGB")
    rec = Image.open(args.recreated).convert("RGB").resize(ref.size, Image.Resampling.LANCZOS)

    strength = max(0.0, min(1.0, args.strength))
    if strength <= 0.0:
        out_img = rec
    else:
        ref_arr = np.asarray(ref, dtype=np.float32)
        rec_arr = np.asarray(rec, dtype=np.float32)
        ref_lab = rgb_to_lab(ref_arr)
        rec_lab = rgb_to_lab(rec_arr)

        matched_lab = rec_lab.copy()
        for ch in range(3):
            r_mean, r_std = float(np.mean(ref_lab[:, :, ch])), float(np.std(ref_lab[:, :, ch])) + 1e-6
            c_mean, c_std = float(np.mean(rec_lab[:, :, ch])), float(np.std(rec_lab[:, :, ch])) + 1e-6
            transferred = (rec_lab[:, :, ch] - c_mean) * (r_std / c_std) + r_mean
            matched_lab[:, :, ch] = (1.0 - strength) * rec_lab[:, :, ch] + strength * transferred

        out_img = Image.fromarray(lab_to_rgb(matched_lab), mode="RGB")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_img.save(out_path)
    print(f"Saved calibrated image ({out_img.size[0]}x{out_img.size[1]}, strength={strength}) to {out_path}")


if __name__ == "__main__":
    main()
