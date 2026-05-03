"""Tool definitions and implementations for the AI agent."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tool schemas (sent to the LLM)
# ---------------------------------------------------------------------------

TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read and return the contents of a file at the given path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute or relative path to the file.",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": (
                "Write text content to a file, creating it (and any missing parent "
                "directories) if it does not exist, or overwriting it if it does."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path where the file should be written.",
                    },
                    "content": {
                        "type": "string",
                        "description": "Text content to write into the file.",
                    },
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": (
                "List the contents of a directory. Returns filenames and whether "
                "each entry is a file or directory."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the directory to list. Defaults to the current working directory.",
                    }
                },
                "required": [],
            },
        },
    },
]


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def read_file(path: str) -> str:
    file = Path(path)
    if not file.exists():
        return f"Error: file not found: {path}"
    if not file.is_file():
        return f"Error: path is not a file: {path}"
    try:
        content = file.read_text(encoding="utf-8")
        logger.debug("read_file: read %d chars from %s", len(content), path)
        return content
    except OSError as exc:
        return f"Error reading file: {exc}"


def write_file(path: str, content: str) -> str:
    file = Path(path)
    try:
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(content, encoding="utf-8")
        logger.debug("write_file: wrote %d chars to %s", len(content), path)
        return f"Successfully wrote {len(content)} characters to {path}"
    except OSError as exc:
        return f"Error writing file: {exc}"


def list_dir(path: str = ".") -> str:
    directory = Path(path)
    if not directory.exists():
        return f"Error: directory not found: {path}"
    if not directory.is_dir():
        return f"Error: path is not a directory: {path}"
    try:
        entries = sorted(directory.iterdir(), key=lambda e: (e.is_file(), e.name))
        lines = []
        for entry in entries:
            kind = "file" if entry.is_file() else "dir"
            size = f"  {entry.stat().st_size}B" if entry.is_file() else ""
            lines.append(f"[{kind}]{size}  {entry.name}")
        result = "\n".join(lines) if lines else "(empty directory)"
        logger.debug("list_dir: listed %d entries in %s", len(entries), path)
        return result
    except OSError as exc:
        return f"Error listing directory: {exc}"


# ---------------------------------------------------------------------------
# Dispatcher — maps tool name → callable
# ---------------------------------------------------------------------------

_DISPATCH: dict[str, Any] = {
    "read_file": read_file,
    "write_file": write_file,
    "list_dir": list_dir,
}


def execute(name: str, arguments: dict[str, Any]) -> str:
    """Execute a tool by name and return its string result."""
    fn = _DISPATCH.get(name)
    if fn is None:
        return f"Error: unknown tool '{name}'"
    logger.info("Executing tool: %s(%s)", name, arguments)
    return fn(**arguments)
