"""Seed HiResCAM config from the best tuning result."""
import csv
import sys
from pathlib import Path

# Allow running from backend/ directory
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.extensions import db

from app import create_app
from app.services.hirescam.config import HiResCAMConfig
from app.services.hirescam.config_store import save_config


def find_best_config(grid_dir: Path) -> dict[str, str]:
    """Find the row with highest focus_metric in summary.csv."""
    summary = grid_dir / "summary.csv"
    if not summary.exists():
        raise FileNotFoundError(f"No summary.csv at {summary}")

    best = None
    with open(summary, newline="") as f:
        for row in csv.DictReader(f):
            if best is None or float(row["focus_metric"]) > float(best["focus_metric"]):
                best = row
    return best


def main() -> None:
    app = create_app()
    with app.app_context():
        storage = Path(app.config["STORAGE_DIR"])
        grid_dir = storage.parent.parent / "outputs" / "hirescam_tuning_grid"

        best = find_best_config(grid_dir)
        config = HiResCAMConfig(
            target_layer_name=best["target_layer"],
            input_size=int(best["input_size"]),
            clip_percentile=float(best["clip_percentile"]),
            smooth_sigma=float(best["smooth_sigma"]),
            top_percent=float(best["top_percent"]),
            colormap=best["colormap"],
        )

        save_config(db.session, config)
        db.session.commit()

        print(f"Applied config from index {best['config_index']}:")
        for k, v in config.to_dict().items():
            print(f"  {k}: {v}")
        print(f"  focus_metric: {best['focus_metric']}")


if __name__ == "__main__":
    main()
