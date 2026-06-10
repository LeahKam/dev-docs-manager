# CLAUDE.md — natural-cli

**AI-powered natural language to CLI command converter.**

## Project Overview

`natural-cli` is a web UI + CLI tool that converts natural language instructions into shell commands using OpenRouter's free AI models (Gemini 2.0 Flash, Kimi K2.6).

### Problem Statement
Users describe what they want to do in plain English; the app generates a shell command they can run. Useful for:
- Quick command generation without manual documentation lookup
- Teaching CLI commands by example
- Automating repetitive shell command construction

## Architecture

### High-Level Flow
1. **User Input** → Natural language instruction (e.g., "list all PDF files in current directory")
2. **LLM Processing** → OpenRouter API + system prompt → Shell command
3. **Output** → Plain-text command (user must verify before running)

### File Structure
```
natural-cli/
├── app.py              # Gradio web UI + core generate_command() logic
├── config.py           # Pydantic Settings (environment variables)
├── main.py             # Typer CLI entry point (web + run commands)
├── system_prompt.md    # LLM system instructions
├── pyproject.toml      # Python project metadata & dependencies
├── .env                # Local environment variables (GITIGNORED)
└── uv.lock             # Locked dependency versions
```

## Tech Stack

| Component | Purpose | Library |
|---|---|---|
| **Web UI** | User interface | `gradio` (6.15.2+) |
| **API Client** | OpenRouter communication | `openai` (2.38.0+) |
| **Configuration** | Environment variable management | `pydantic-settings` (2.0.0+) |
| **CLI Framework** | Command-line interface | `typer` (0.12.0+) |

### External APIs
- **OpenRouter** (`https://api.openrouter.ai/v1`)
  - Free models: `google/gemini-2.0-flash-exp:free`, `moonshotai/kimi-k2.6:free`
  - Requires `OPENROUTER_API_KEY` environment variable
  - Rate-limited on free tier

## Key Files & Modules

### `app.py` — Web UI & Core Logic
**Purpose:** Gradio web interface + main `generate_command()` function

**Key Functions:**
- `_get_client()` — Creates OpenAI client (lazy initialization, avoids early API validation)
- `generate_command(instruction, model, temperature)` — Calls OpenRouter API, returns shell command
- `demo` (Gradio Blocks) — UI layout (textbox for instruction, dropdown for model, slider for temperature, output textbox)

**Error Handling:**
- Missing `OPENROUTER_API_KEY` → returns error message
- API errors caught as `APIError` → returned as plain text (no exception raised)

**Flow:**
1. User clicks "Generate" button
2. `on_generate()` callback calls `generate_command()`
3. Response written to output textbox

### `config.py` — Settings & Environment Variables
**Purpose:** Centralized configuration using Pydantic

**Settings Class Fields:**
| Field | Env Variable | Default |
|---|---|---|
| `openrouter_api_key` | `OPENROUTER_API_KEY` | `""` (required) |
| `openrouter_base_url` | `OPENROUTER_BASE_URL` | `https://api.openrouter.ai/v1` |
| `default_model` | `DEFAULT_MODEL` | `moonshotai/kimi-k2.6:free` |
| `default_temperature` | `DEFAULT_TEMPERATURE` | `0.0` |
| `max_tokens` | `MAX_TOKENS` | `200` |

**Config Source Priority:**
1. Environment variables (highest priority)
2. `.env` file (lower priority)
3. Defaults in Settings class (lowest priority)

**Usage:** Import `settings` singleton from `config.py` anywhere in the app.

### `main.py` — CLI Entry Point
**Purpose:** Typer command-line interface

**Commands:**
```bash
uv run python main.py web                          # Launch Gradio web UI
uv run python main.py run "create a virtualenv"    # Run CLI mode
```

**Parameters for `run` command:**
- `instruction` (positional, required) — Natural language instruction
- `--model` (optional, default: `moonshotai/kimi-k2.6:free`)
- `--temperature` (optional, default: `0.0`)

**Output:** Shell command printed to stdout (can be piped/captured)

### `system_prompt.md` — LLM Instructions
**Purpose:** System-level instructions for the LLM to follow

**Contains:**
- Context: "You are a shell command generator"
- Instructions: Format, safety guidelines, handling edge cases
- Examples: Common natural language → command mappings

**When to Edit:** Adjust LLM behavior (e.g., add safety constraints, change output format, add specific command examples).

## Setup & Running

### Prerequisites
- **Python 3.14+** (as per `pyproject.toml`)
- **uv** package manager (installed globally)
- **OpenRouter API Key** (get free key at https://openrouter.ai)

### First-Time Setup
```bash
# 1. Clone/enter repo
cd natural-cli

# 2. Set environment variable (Windows)
setx OPENROUTER_API_KEY "sk-or-v1-xxxxx"

# 3. Install dependencies
uv sync

# 4. (Optional) Create .env file
echo "OPENROUTER_API_KEY=sk-or-v1-xxxxx" > .env
```

### Running

**Web UI:**
```bash
uv run python app.py
# or
uv run python main.py web
```
Opens Gradio at `http://localhost:7860`

**CLI:**
```bash
uv run python main.py run "list all .py files in current directory"
uv run python main.py run "create a backup of my home folder" --model google/gemini-2.0-flash-exp:free --temperature 0.1
```

**Output captured to variable (Bash):**
```bash
CMD=$(uv run python main.py run "restart the docker daemon")
echo "$CMD"  # Review before running
eval "$CMD"  # Execute
```

## Coding Conventions

### Style Guidelines
- **No comments** in code (code is self-documenting; comments only for non-obvious WHY)
- **Full type hints** on all function signatures
- **Explicit UTF-8 encoding** for file I/O (`open(..., encoding="utf-8")`)
- **Pathlib** for file paths (never raw string paths)
- **f-strings** for formatting
- **Pydantic** for data validation/config

### Error Handling
- Catch external errors (API, I/O) and return user-friendly messages
- Don't raise exceptions in `generate_command()` — return error strings
- Missing API keys should be caught early with clear messaging

### Imports
```python
from pathlib import Path  # File paths
from openai import OpenAI, APIError  # OpenRouter client
import gradio as gr  # Web UI
from pydantic_settings import BaseSettings  # Config
import typer  # CLI
```

## Common Development Tasks

### Adding a New Configuration Option
1. Add field to `Settings` class in `config.py` with validation alias
2. Update `.env.example` with new variable
3. Reference in app via `settings.<field_name>`

### Modifying LLM Behavior
1. Edit `system_prompt.md` (affects all future generations)
2. Test in Gradio UI or CLI
3. Commit changes with explanation of new behavior

### Adding a New OpenRouter Model
1. Find model ID at https://openrouter.ai/models
2. Add to Gradio dropdown in `app.py` (line 37-38) or update default in `config.py`
3. Update `main.py` default if desired

### Testing a Command
```bash
# Generate command
uv run python main.py run "describe a command" > /tmp/cmd.sh

# Review
cat /tmp/cmd.sh

# Run if safe
bash /tmp/cmd.sh
```

## Dependency Management

### Install/Update Dependencies
```bash
uv sync          # Install all from lock file
uv add gradio    # Add new package
uv remove typer  # Remove package
uv lock          # Update lock file
```

### Current Dependencies
- `gradio` → Web UI
- `openai` → OpenRouter API client
- `pydantic-settings` → Config management
- `typer` → CLI framework

## Git Workflow

### Branch Strategy
- **main** — clean, stable state
- **feature/\*** — feature development branches
- Always ask before committing or pushing

### Before Committing
- Test web UI in browser
- Test CLI with several instructions
- Run `uv sync` to ensure lock file matches

### Commit Messages
- One sentence describing the change
- Reference the issue/feature if applicable
- Example: `Add temperature slider to Gradio UI` or `Use free OpenRouter models by default`

## Troubleshooting

### "OPENROUTER_API_KEY not set"
- **Windows (temporary):** `set OPENROUTER_API_KEY=sk-or-v1-xxxxx` then run
- **Windows (permanent):** `setx OPENROUTER_API_KEY "sk-or-v1-xxxxx"` (restart terminal)
- **Linux/Mac:** `export OPENROUTER_API_KEY="sk-or-v1-xxxxx"` or add to `.bashrc`
- **Via .env file:** Create `.env` in repo root with `OPENROUTER_API_KEY=sk-or-v1-xxxxx`

### API Rate Limiting
- Free models have rate limits on OpenRouter
- Solution: Increase delay between requests, upgrade API tier, or use different model
- Check https://openrouter.ai/status for service status

### Gradio Port Already in Use
```bash
# Find process using port 7860
lsof -i :7860

# Or use different port
PORT=8000 uv run python app.py
```

## Future Enhancements

Potential improvements (not currently implemented):
- Command history persistence
- Syntax highlighting for generated commands
- Multi-step command generation
- Local fallback LLM (Ollama)
- Command preview with `--dry-run`
- Integration with shell histories

## Resources

- **OpenRouter Docs:** https://openrouter.ai/docs
- **Gradio Docs:** https://www.gradio.app/
- **Typer Docs:** https://typer.tiangolo.com/
- **Pydantic Settings:** https://docs.pydantic.dev/latest/concepts/settings/
