"""Agent loop, sends messages to the LLM, handles tool calls, and loops until done."""

from __future__ import annotations

import json
import logging
from typing import Any

from openai import OpenAI

from claude_code import tools

logger = logging.getLogger(__name__)

# Maximum number of tool-call rounds before we stop to avoid infinite loops.
MAX_ITERATIONS = 20


def run(prompt: str, client: OpenAI, model: str) -> str:
    """
    Run the agent loop for a given prompt.

    Sends the prompt to the model, executes any tool calls the model requests,
    feeds the results back, and repeats until the model returns a plain text
    response (no more tool calls) or we hit MAX_ITERATIONS.

    Returns the final text response.
    """
    messages: list[dict[str, Any]] = [{"role": "user", "content": prompt}]

    for iteration in range(MAX_ITERATIONS):
        logger.debug("Agent iteration %d — sending %d messages", iteration + 1, len(messages))

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools.TOOL_SCHEMAS,
            tool_choice="auto",
        )

        if not response.choices:
            raise RuntimeError("LLM returned an empty response.")

        message = response.choices[0].message

        # No tool calls → the model is done; return its text.
        if not message.tool_calls:
            logger.debug("Agent finished after %d iteration(s)", iteration + 1)
            return message.content or ""

        # Append the assistant turn (with tool_calls) to the history.
        messages.append(message.model_dump(exclude_unset=True))

        # Execute every tool the model requested and collect results.
        for call in message.tool_calls:
            name = call.function.name
            try:
                arguments = json.loads(call.function.arguments)
            except json.JSONDecodeError as exc:
                result = f"Error: could not parse tool arguments: {exc}"
                logger.warning("Bad tool arguments for %s: %s", name, exc)
            else:
                result = tools.execute(name, arguments)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": result,
                }
            )

    raise RuntimeError(
        f"Agent exceeded the maximum of {MAX_ITERATIONS} iterations without a final response."
    )
