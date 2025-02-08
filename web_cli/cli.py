import argparse
import logging
import sys
import json
from web_engine.parsers import get_parser
from web_engine.engine import execute_query


def setup_logging(log_level, log_file=None):
    """Configure logging based on the specified level and output file."""
    log_levels = {
        "error": logging.ERROR,
        "warning": logging.WARNING,
        "info": logging.INFO,
        "debug": logging.DEBUG
    }
    logging.basicConfig(
        level=log_levels.get(log_level, logging.ERROR),
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file) if log_file else logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    parser = argparse.ArgumentParser(description="OXPath-like JSON Query CLI")
    parser.add_argument("-q", "--query", default="query.json5", required=False, help="Path to the query file")
    parser.add_argument("-o", "--output", default="sitters.json", required=False, help="Output file name")
    parser.add_argument(
        "-f", "--format", default="json5", choices=["json5", "yaml"],
        help="Query language format (default: json5)"
    )
    parser.add_argument(
        "-l", "--log-level", default="info", choices=["error", "warning", "info", "debug"],
        help="Logging level (default: error)"
    )
    parser.add_argument("--log-file", help="Path to the log file (default: stdout)")
    args = parser.parse_args()

    # Set up logging
    setup_logging(args.log_level, args.log_file)

    try:
        # Get the appropriate parser
        parser_fn = get_parser(args.format)
        query = parser_fn(args.query)

        # Execute the query
        results = execute_query(query)

        # Save the results
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        logging.info(f"Results saved to {args.output}")
    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)


if __name__ == "__main__":
    main()

