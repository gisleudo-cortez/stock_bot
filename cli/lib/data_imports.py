import polars as pl
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data/")
os.makedirs(DATA_DIR, exist_ok=True)


def load_local() -> pl.DataFrame:
    print(DATA_DIR)
    return pl.read_csv(DATA_DIR + "test_prices.csv")
