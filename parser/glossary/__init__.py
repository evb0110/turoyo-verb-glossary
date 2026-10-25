"""Lossless, formatting-aware reader for the glossary's Word volumes."""

from .parse import parse_volumes, write_glossary

__all__ = ["parse_volumes", "write_glossary"]
