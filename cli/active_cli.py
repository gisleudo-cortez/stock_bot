import argparse

from lib.active_class import Active


def main() -> None:
    parser = argparse.ArgumentParser(description="Active CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    active_parser = subparsers.add_parser(
        name="active", help="Initialize a active for monitoring"
    )
    active_parser.add_argument(
        "check", help="Check if and active is Available for monitoring"
    )

    tracking_parser = subparsers.add_parser("track", help="Start tracking of an active")
    # add a argument with time intervals to track (todo.txt)

    args = parser.parse_args()
    match args.command:
        case "check":
            active = Active(args.active)
            print()
        case "track":
            # start loop to monitoring
            print("To be implemented")
            NotImplementedError()
        case _:
            parser.print_help()


if __name__ == "__main__":
    main()
