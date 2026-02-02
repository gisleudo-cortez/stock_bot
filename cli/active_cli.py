import argparse

from lib.active_class import Active


def main() -> None:
    parser = argparse.ArgumentParser(description="Active CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    active_parser = subparsers.add_parser(
        name="active", help="Initialize a active for monitoring"
    )
    active_parser.add_argument("active", help="active to be monitored")

    args = parser.parse_args()
    match args.command:
        case "active":
            active = Active(args.active)
            print()
        case _:
            parser.print_help()


if __name__ == "__main__":
    main()
