import argparse
import time
import sys
from typing import List
from lib.active_class import Active


def parse_interval(interval_str: str) -> int:
    """Parses '15m', '1h', '30s' into seconds."""
    unit = interval_str[-1].lower()
    value = int(interval_str[:-1])
    if unit == "s":
        return value
    if unit == "m":
        return value * 60
    if unit == "h":
        return value * 3600
    if unit == "d":
        return value * 86400
    return int(interval_str)  # Default to seconds if no unit


def track_assets(tickers: List[str], interval: int):
    """Main synchronous tracking loop."""
    print("--- Starting Active Tracker ---")
    print(f"Tickers: {', '.join(tickers)}")
    print(f"Interval: {interval} seconds")
    print("-------------------------------")

    # Initialize Actives
    actives = [Active(t) for t in tickers]

    try:
        while True:
            start_time = time.time()
            print(f"\n[Cycle Start: {time.strftime('%H:%M:%S')}]")

            for active in actives:
                active.refresh_data()
                # Placeholder for strategy logic
                # if active.trend_angle > 45: active.notify("Strong Uptrend")

            elapsed = time.time() - start_time
            sleep_time = max(0, interval - elapsed)

            print(f"[Cycle End] Sleeping for {sleep_time:.1f}s...")
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\n--- Stopping Tracker ---")
        sys.exit(0)


def main() -> None:
    parser = argparse.ArgumentParser(description="Active CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: active (Single Check)
    active_parser = subparsers.add_parser(
        name="active", help="Initialize a active for monitoring"
    )
    active_parser.add_argument(
        "ticker", help="Check if an active is Available for monitoring"
    )

    # Command: track (Continuous Loop)
    tracking_parser = subparsers.add_parser("track", help="Start tracking of actives")
    tracking_parser.add_argument(
        "tickers", nargs="+", help="List of tickers to track (e.g. AAPL MSFT)"
    )
    tracking_parser.add_argument(
        "-i", "--interval", default="15m", help="Update interval (e.g., 1m, 15m, 1h)"
    )

    args = parser.parse_args()

    match args.command:
        case (
            "active"
        ):  # Renamed from 'check' in your original code to match parser name logic
            active = Active(args.ticker)
            print(active)
        case "track":
            interval_sec = parse_interval(args.interval)
            track_assets(args.tickers, interval_sec)
        case _:
            parser.print_help()


if __name__ == "__main__":
    main()
