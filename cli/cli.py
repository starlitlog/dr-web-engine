import typer
import logging
import json
from engine.web_engine.parsers import get_parser
from engine.web_engine.engine import execute_query
from engine.web_engine.base.playwright_browser import PlaywrightClient
from .plugin_cli import plugin_app


def setup_logging(log_level: str, log_file: str = None):
    """Configure logging based on the specified level and output file."""
    log_levels = {
        "error": logging.ERROR,
        "warning": logging.WARNING,
        "info": logging.INFO,
        "debug": logging.DEBUG
    }
    handlers = [logging.StreamHandler()]  # Default to stream logging

    if log_file:
        log_file_path = str(log_file)  # Explicitly convert to string
        handlers.append(logging.FileHandler(log_file_path))

    logging.basicConfig(
        level=log_levels.get(log_level, logging.ERROR),
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=handlers
    )


app = typer.Typer(help="DR Web Engine - Data Retrieval Engine")

# Add plugin management commands
app.add_typer(plugin_app)


@app.command()
def run(
    query: str = typer.Option(..., "-q", "--query", help="Path to the query file"),
    output: str = typer.Option(..., "-o", "--output", help="Output file name"),
    query_format: str = typer.Option("json5", "-f", "--format", help="Query language format (default: json5)"),
    log_level: str = typer.Option("error", "-l", "--log-level", help="Logging level (default: error)"),
    log_file: str = typer.Option(None, "--log-file", help="Path to the log file (default: stdout)"),
    xvfb: bool = typer.Option(False, "--xvfb", help="Launch browser in headless mode using Xvfb")
):
    """OXPath-like JSON Query CLI"""
    # Set up logging
    setup_logging(log_level, log_file)

    try:
        # Get the appropriate parser
        parser_fn = get_parser(query_format)
        query = parser_fn(query)
        browser = PlaywrightClient(xvfb)

        # Execute the query
        results = execute_query(query, browser)

        # Save the results
        with open(output, "w") as f:
            json.dump(results, f, indent=2)
        logging.info(f"Results saved to {output}")
    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)


if __name__ == "__main__":
    app()
