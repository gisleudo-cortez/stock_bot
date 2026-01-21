import sys
from pathlib import Path

# 1. MOVE THIS TO THE TOP
# This ensures the root 'stock_bot/' is in the search path BEFORE imports run
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# 2. NOW PERFORM THE IMPORT
from lib.active_class import Active


def test_polars_naming():
    # Note: Ensure .env is in the root for Active to initialize
    stock = Active("AAPL")
    stock.refresh_data()

    df = stock.to_polars()

    # Verify columns exist as requested
    assert "current_price" in df.columns
    assert "updated_at" in df.columns

    print("\n--- Polars Structured Data ---")
    print(df)


def run_test():
    print("--- Running Active Class Test ---")

    # Test 1: Successful Initialization
    try:
        apple = Active("AAPL")
        print(f"✅ Success: Initialized {apple.ticker}")
    except Exception as e:
        print(f"❌ Failed Test 1: {e}")

    # Test 2: Requirement Validation
    try:
        empty = Active()  # type: ignore
        print("❌ Failed Test 2: Class allowed empty initialization")
    except TypeError:
        print("✅ Success: Caught missing ticker error")

    test_polars_naming()


if __name__ == "__main__":
    run_test()
