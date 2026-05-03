"""Command-line entry point."""

from __future__ import annotations

import argparse
import logging
import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

from claudecode import agent

DEFAULT_MODEL = "anthropic/claude-haiku-4-5"
DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="claudecode",
        description="A minimal AI coding assistant powered by an OpenAI-compatible LLM.",
    )
    parser.add_argument(
        "-p", "--prompt",
        required=True,
        metavar="PROMPT",
        help="The prompt to send to the assistant.",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("CLAUDE_CODE_MODEL", DEFAULT_MODEL),
        metavar="MODEL",
        help=f"Model identifier to use (default: {DEFAULT_MODEL}).",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging.",
    )
    return parser


def configure_logging(debug: bool) -> None:
    level = logging.DEBUG if debug else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(levelname)s  %(name)s  %(message)s",
        stream=sys.stderr,
    )


def main() -> None:
    load_dotenv()  # Load .env if present, no-op if it doesn't exist.

    parser = build_parser()
    args = parser.parse_args()

    configure_logging(args.debug)

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        sys.exit("Error: OPENROUTER_API_KEY is not set. Add it to your .env file or export it.")

    base_url = os.getenv("OPENROUTER_BASE_URL", DEFAULT_BASE_URL)

    client = OpenAI(api_key=api_key, base_url=base_url)

    try:
        result = agent.run(prompt=args.prompt, client=client, model=args.model)
        print(result)
    except RuntimeError as exc:
        sys.exit(f"Error: {exc}")


if __name__ == "__main__":
    main()
