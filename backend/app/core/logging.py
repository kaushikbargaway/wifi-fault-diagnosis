"""Logging configuration for the application."""

import logging
import sys


def configure_logging(level: int = logging.INFO) -> None:
    """Configure root logger to output structured lines to stdout."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        stream=sys.stdout,
    )
