# claudecode

A minimal AI coding assistant that runs in your terminal. It connects to an LLM via [OpenRouter](https://openrouter.ai/) and can read files, write files, and list directories on your machine to help you with coding tasks.

## How it works

You give it a prompt. It sends that to the model. If the model needs to look at files, it calls one of the available tools — and the agent loop automatically executes the tool, feeds the result back, and keeps going until the model has a final answer.

```
you  ──prompt──▶  agent ──▶  LLM
                    ▲          │
                    │    tool_call?
                    │          │
                  result  ◀──tool
```

## Requirements

- Python 3.14+
- [`uv`](https://docs.astral.sh/uv/) — used to manage dependencies and run the project
- An [OpenRouter](https://openrouter.ai/) API key

## Setup

```sh
# 1. Clone / download the project, then enter its directory
cd claudecode

# 2. Copy the example env file and add your API key
cp .env.example .env
# Edit .env and set OPENROUTER_API_KEY

# 3. Install dependencies
uv sync
```

## Usage

```sh
uv run claudecode --prompt "What files are in the current directory?"
uv run claudecode --prompt "Read main.py and explain what it does"
uv run claudecode --prompt "Create a hello.py file that prints Hello, world"
```

**Options**

| Flag | Default | Description |
|------|---------|-------------|
| `-p`, `--prompt` | *(required)* | The prompt to send |
| `--model` | `anthropic/claude-haiku-4-5` | Any OpenRouter model string |
| `--debug` | off | Print debug logs to stderr |

The model can also be set via the `CLAUDE_CODE_MODEL` env variable.

## Project structure

```
src/
  claudecode/
    cli.py      # Argument parsing and startup
    agent.py    # Agent loop — sends messages, handles tool calls, loops
    tools.py    # Tool definitions (schemas) and implementations
pyproject.toml  # Dependencies and `claudecode` entry point
.env.example    # Environment variable template
```

## Available tools

| Tool | What it does |
|------|-------------|
| `read_file` | Read a file and return its contents |
| `write_file` | Write (or overwrite) a file, creating parent dirs as needed |
| `list_dir` | List the contents of a directory |

Adding a new tool means adding its schema to `TOOL_SCHEMAS` and its implementation to `_DISPATCH` in `tools.py` — nothing else needs to change.
