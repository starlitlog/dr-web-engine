import typer
import logging
import json
import os

# Fix typer Parameter.make_metavar compatibility issue
import click.core
_original_make_metavar = click.core.Parameter.make_metavar

def _patched_make_metavar(self, ctx=None):
    if ctx is None:
        return _original_make_metavar(self, None)  # Provide default context
    return _original_make_metavar(self, ctx)

click.core.Parameter.make_metavar = _patched_make_metavar
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


# Main callback that handles backward compatibility
@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    query: str = typer.Option(None, "-q", "--query", help="Path to the query file"),
    output: str = typer.Option(None, "-o", "--output", help="Output file name"),
    query_format: str = typer.Option("json5", "-f", "--format", help="Query language format (default: json5)"),
    log_level: str = typer.Option("error", "-l", "--log-level", help="Logging level (default: error)"),
    log_file: str = typer.Option(None, "--log-file", help="Path to the log file (default: stdout)"),
    xvfb: bool = typer.Option(False, "--xvfb", help="Launch browser in headless mode using Xvfb")
):
    """DR Web Engine - Data Retrieval Engine"""
    # If no subcommand was invoked and we have query/output, run the extraction
    if not ctx.invoked_subcommand and query and output:
        run_extraction(query, output, query_format, log_level, log_file, xvfb)


def run_extraction(query, output, query_format, log_level, log_file, xvfb):
    """Execute the data extraction query"""
    import os
    from pathlib import Path
    
    # Set up logging
    setup_logging(log_level, log_file)

    try:
        # Check if query file exists
        if not Path(query).exists():
            typer.secho(f"❌ Error: Query file '{query}' not found", fg=typer.colors.RED, err=True)
            raise typer.Exit(1)
        
        # Get the appropriate parser
        parser_fn = get_parser(query_format)
        parsed_query = parser_fn(query)
        
        # Create browser instance
        browser = PlaywrightClient(xvfb)

        # Execute the query
        typer.secho(f"🔄 Executing query from '{query}'...", fg=typer.colors.CYAN)
        results = execute_query(parsed_query, browser)

        # Save the results
        with open(output, "w") as f:
            json.dump(results, f, indent=2)
        
        typer.secho(f"✅ Results saved to '{output}'", fg=typer.colors.GREEN)
        
    except FileNotFoundError as e:
        typer.secho(f"❌ File not found: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)
    except json.JSONDecodeError as e:
        typer.secho(f"❌ Invalid JSON in query file: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)
    except KeyError as e:
        typer.secho(f"❌ Missing required field in query: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)
    except typer.Exit:
        raise  # Re-raise Exit exceptions
    except Exception as e:
        if log_level == "debug":
            logging.error(f"Unexpected error: {e}", exc_info=True)
        else:
            typer.secho(f"❌ Error: {e}", fg=typer.colors.RED, err=True)
            typer.secho("💡 Use --log-level debug for more details", fg=typer.colors.YELLOW)
        raise typer.Exit(1)


@app.command()
def run(
    query: str = typer.Option(..., "-q", "--query", help="Path to the query file"),
    output: str = typer.Option(..., "-o", "--output", help="Output file name"),
    query_format: str = typer.Option("json5", "-f", "--format", help="Query language format (default: json5)"),
    log_level: str = typer.Option("error", "-l", "--log-level", help="Logging level (default: error)"),
    log_file: str = typer.Option(None, "--log-file", help="Path to the log file (default: stdout)"),
    xvfb: bool = typer.Option(False, "--xvfb", help="Launch browser in headless mode using Xvfb")
):
    """Execute a data extraction query"""
    run_extraction(query, output, query_format, log_level, log_file, xvfb)




# Version command
@app.command()
def version():
    """Show version information"""
    from importlib.metadata import version as get_version
    try:
        pkg_version = get_version("dr-web-engine")
    except:
        pkg_version = "1.0.0"
    
    typer.secho(f"DR Web Engine v{pkg_version}", fg=typer.colors.GREEN, bold=True)
    typer.secho("A data retrieval engine based on Playwright", fg=typer.colors.CYAN)
    typer.secho("Homepage: https://github.com/starlitlog/dr-web-engine", fg=typer.colors.BLUE)


if __name__ == "__main__":
    app()
