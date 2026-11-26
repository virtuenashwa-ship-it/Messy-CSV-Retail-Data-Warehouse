import logging
from pathlib import Path
import pandas as pd
from config.settings import RAW_DIR

logger = logging.getLogger(__name__)


def load_raw_csvs(raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    """Read all raw retail CSV files into a single staging DataFrame."""
    csv_files = sorted(raw_dir.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {raw_dir}")

    frames = []
    for file_path in csv_files:
        df = pd.read_csv(file_path, dtype=str)
        df["source_file"] = file_path.name
        frames.append(df)
        logger.info("Loaded %d raw rows from %s", len(df), file_path.name)

    return pd.concat(frames, ignore_index=True)
