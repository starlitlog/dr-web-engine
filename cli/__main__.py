#!/usr/bin/env python
"""
Entry point for dr-web-engine CLI.
This file ensures Windows compatibility.
"""

from cli.cli import app

if __name__ == "__main__":
    app()