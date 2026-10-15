"""Logging utilities."""

import logging

def setup_logging(level: str = "INFO") -> None:
# def setup_logging() -> None:
    """
    Setup logging configuration.

    Args:
        level (str): Logging level. Default is "DEBUG".

    Returns:
        None
    """
    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )