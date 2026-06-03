import pandas as pd
from pathlib import Path

_DEFAULT_CSV = Path.cwd() / "app" / "testdata.csv"

def _load_default() -> pd.DataFrame | None:
    if _DEFAULT_CSV.exists():
        return pd.read_csv(_DEFAULT_CSV)
    return None

current_df: pd.DataFrame | None = _load_default()


def save_dataset(df: pd.DataFrame) -> None:
    global current_df
    current_df = df


def get_dataset() -> pd.DataFrame | None:
    return current_df