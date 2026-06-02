"""CLI tool for HiResCAM tuning experiments.

Generates heatmaps across a grid of configurations and produces
structured output (images + metadata.json + summary.csv).

Usage:
    python scripts/run_hirescam_tuning.py \\
        --model runs/ecg_cls/weights/best.pt \\
        --image data/sample_ecg.png \\
        --output outputs/hirescam_tuning \\
        --input-sizes 1600 2048 \\
        --target-layers last_conv second_last_conv third_last_conv \\
        --smooth-sigmas 0 1.0 1.5 \\
        --top-percents 15 20 25 \\
        --clip-percentiles 99 99.5 \\
        --colormaps turbo inferno \\
        --target-class-mode predicted_class
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from itertools import product
from pathlib import Path

import cv2
import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="HiResCAM tuning experiment runner"
    )
    parser.add_argument("--model", required=True, help="Path to YOLO .pt weights")
    parser.add_argument("--image", required=True, help="Path to input ECG image")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument(
        "--input-sizes", nargs="+", type=int, default=[1600],
        help="Input sizes to test (default: [1600])"
    )
    parser.add_argument(
        "--target-layers", nargs="+", default=["last_conv"],
        help="Target layers (default: [last_conv])"
    )
    parser.add_argument(
        "--smooth-sigmas", nargs="+", type=float, default=[1.0],
        help="Gaussian smooth sigmas (default: [1.0])"
    )
    parser.add_argument(
        "--top-percents", nargs="+", type=float, default=[20.0],
        help="Top percent thresholds (default: [20.0])"
    )
    parser.add_argument(
        "--clip-percentiles", nargs="+", type=float, default=[99.0],
        help="Clip percentiles (default: [99.0])"
    )
    parser.add_argument(
        "--colormaps", nargs="+", default=["inferno"],
        help="Colormaps to test (default: [inferno])"
    )
    parser.add_argument(
        "--target-class-mode", default="predicted_class",
        choices=["predicted_class", "fixed"],
        help="How to choose target class (default: predicted_class)"
    )
    parser.add_argument(
        "--target-class-idx", type=int, default=0,
        help="Fixed class index (used when target-class-mode=fixed)"
    )
    parser.add_argument(
        "--device", default="cpu", help="Device: cpu or cuda (default: cpu)"
    )
    parser.add_argument(
        "--overlay-alpha", type=float, default=0.45,
        help="Overlay transparency (default: 0.45)"
    )
    return parser.parse_args()


def run_experiment(
    model_path: str,
    image_path: str,
    output_dir: Path,
    config: dict,
    config_idx: int,
    overlay_alpha: float,
    device: str,
) -> dict | None:
    """Run a single experiment configuration.

    Returns:
        Metadata dict for summary.csv, or None on failure.
    """
    from PIL import Image

    from app.services.hirescam.colormap import array_to_png
    from app.services.hirescam.evaluator import evaluate_explanation
    from app.services.hirescam.generator_v2 import generate_hirescam_v2
    from app.services.hirescam.overlay import compose_overlay
    from app.services.hirescam.postprocess import postprocess_heatmap
    from app.services.inference.loader import load_model

    try:
        model = load_model(Path(model_path))

        # Determine target class
        if config["target_class_mode"] == "predicted_class":
            result = model.predict(image_path, verbose=False)
            probs = result[0].probs
            target_class_idx = int(probs.top1)
            confidence = float(probs.top1conf)
        else:
            target_class_idx = config["target_class_idx"]
            confidence = None

        # Generate heatmap
        heatmap, lb_params, metadata = generate_hirescam_v2(
            model,
            image_path,
            target_class_idx,
            target_layer_name=config["target_layer"],
            input_size=config["input_size"],
            device=device,
        )

        # Post-process
        processed = postprocess_heatmap(
            heatmap,
            lb_params,
            clip_percentile=config["clip_percentile"],
            smooth_sigma=config["smooth_sigma"],
            top_percent=config["top_percent"],
            colormap=config["colormap"],
        )

        # Save outputs
        cfg_dir = output_dir / f"config_{config_idx:03d}"
        cfg_dir.mkdir(parents=True, exist_ok=True)

        # Original image
        orig = cv2.imread(image_path)
        cv2.imwrite(
            str(cfg_dir / "original.png"),
            cv2.cvtColor(orig, cv2.COLOR_BGR2RGB),
        )

        # Raw heatmap
        np.save(str(cfg_dir / "heatmap_raw.npy"), processed["heatmap_raw"])

        # Normalized heatmap as PNG
        norm_uint8 = (processed["heatmap_norm"] * 255).astype(np.uint8)
        Image.fromarray(norm_uint8, mode="L").save(cfg_dir / "heatmap_norm.png")

        # Colored heatmap
        Image.fromarray(
            processed["heatmap_colored"], mode="RGB"
        ).save(cfg_dir / "heatmap_colored.png")

        # Overlay
        colored_bytes = array_to_png(
            processed["heatmap_norm"], colormap=config["colormap"]
        )
        overlay_bytes = compose_overlay(image_path, colored_bytes)
        with open(cfg_dir / "overlay.png", "wb") as f:
            f.write(overlay_bytes)

        # Mask top area
        mask_uint8 = (processed["mask_top_area"] * 255).astype(np.uint8)
        Image.fromarray(mask_uint8, mode="L").save(cfg_dir / "mask_top_area.png")

        # Metadata
        metadata.update({
            "config_index": config_idx,
            "clip_percentile": config["clip_percentile"],
            "smooth_sigma": config["smooth_sigma"],
            "top_percent": config["top_percent"],
            "colormap": config["colormap"],
            "overlay_alpha": overlay_alpha,
        })
        with open(cfg_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        # Evaluate
        status, focus_metric = evaluate_explanation(
            processed["heatmap_norm"], confidence=confidence
        )
        metadata["explanation_status"] = status
        metadata["focus_metric"] = focus_metric

        return metadata

    except Exception as e:
        print(f"  [ERROR] Config {config_idx}: {e}", file=sys.stderr)
        return None


def main():
    args = parse_args()

    if not os.path.isfile(args.model):
        print(f"Error: Model file not found: {args.model}", file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(args.image):
        print(f"Error: Image file not found: {args.image}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build experiment grid
    grid = list(product(
        args.input_sizes,
        args.target_layers,
        args.smooth_sigmas,
        args.top_percents,
        args.clip_percentiles,
        args.colormaps,
    ))

    print(f"Running {len(grid)} experiments...")
    print(f"  Model: {args.model}")
    print(f"  Image: {args.image}")
    print(f"  Output: {output_dir}")
    print(f"  Device: {args.device}")

    results = []
    for idx, (inp_size, tgt_layer, smooth, top_pct, clip_pct, cmap) in enumerate(grid, 1):
        config = {
            "input_size": inp_size,
            "target_layer": tgt_layer,
            "smooth_sigma": smooth,
            "top_percent": top_pct,
            "clip_percentile": clip_pct,
            "colormap": cmap,
            "target_class_mode": args.target_class_mode,
            "target_class_idx": args.target_class_idx,
        }
        print(
            f"  [{idx}/{len(grid)}] input={inp_size} layer={tgt_layer} "
            f"smooth={smooth} top={top_pct} clip={clip_pct} cmap={cmap}"
        )

        meta = run_experiment(
            args.model, args.image, output_dir, config, idx,
            args.overlay_alpha, args.device,
        )
        if meta:
            results.append(meta)

    # Write summary.csv
    if results:
        csv_path = output_dir / "summary.csv"
        fieldnames = list(results[0].keys())
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"\nDone. {len(results)}/{len(grid)} experiments succeeded.")
        print(f"Summary: {csv_path}")
    else:
        print("\nNo experiments succeeded.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
