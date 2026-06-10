# natural-cli — AI Agent Guide

## Project Overview

A web UI + CLI tool that converts natural-language instructions into shell commands using OpenRouter's AI API.

## Architecture

```
app.py          → Gradio web UI (user interface)
config.py       → Pydantic settings (env vars + .env file)
main.py         → Typer CLI entry point (web + run commands)
system_prompt.md → LLM system prompt
pyproject.toml  → Python project metadata & deps
```

### Data Flow

1. User types instruction in Gradio UI (or via CLI)
2. `generate_command()` sends instruction + system prompt to OpenRouter via OpenAI SDK
3. Response is returned (a shell command as plain text)

## Tech Stack

| Library | Purpose |
|---|---|
| `gradio` | Web UI |
| `openai` | OpenRouter API client (OpenAI-compatible) |
| `pydantic-settings` | Configuration from env vars + `.env` file |
| `typer` | CLI entry point |

## Key Files

### `config.py`
- `Settings` class using Pydantic `BaseSettings`
- Reads from environment variables and `.env` file
- Fields: `OPENROUTER_API_KEY`, `OPENROUTER_BASE_URL`, `DEFAULT_MODEL`, `DEFAULT_TEMPERATURE`, `MAX_TOKENS`

### `app.py`
- `_get_client()` — creates OpenAI client lazily (avoids SDK validation at import time)
- `generate_command()` — main function, called by both UI and CLI
- Gradio `demo` Blocks UI at module level

### `main.py`
- Two typer commands:
  - `web` — launches Gradio UI
  - `run` — takes instruction arg, prints command to stdout

## Coding Conventions

- **No comments** in code unless absolutely necessary
- **Full type hints** on all function signatures
- **Pydantic** for configuration and data models
- **pathlib** for file paths, never `open("path")` without encoding
- **f-strings** for string formatting
- **Explicit `utf-8` encoding** for file I/O

## How to Run

```bash
uv run python app.py               # Web UI
uv run python main.py web          # Same
uv run python main.py run "..."    # CLI mode
```

## Dependencies

Manage with `uv`:
```bash
uv sync          # Install all deps
uv add <pkg>     # Add new dependency
uv remove <pkg>  # Remove dependency
```

## Branch Strategy

- `main` — default branch, clean state
- `feature/*` — feature branches for development
- Always ask before committing or pushing
