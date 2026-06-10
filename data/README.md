# natural-cli

Convert natural-language instructions into shell commands using AI.

## Setup

```bash
# Set your OpenRouter API key
setx OPENROUTER_API_KEY "sk-or-v1-..."

# Install dependencies
uv sync
```

## Usage

### Web UI

```bash
uv run python app.py
```

### CLI

```bash
uv run python main.py run "create a python virtualenv and install requests"
uv run python main.py run "list all pdf files in current directory"
```

## Configuration

All settings are controlled via environment variables:

| Variable | Default | Description |
|---|---|---|
| `OPENROUTER_API_KEY` | — | Your OpenRouter API key |
| `OPENROUTER_BASE_URL` | `https://api.openrouter.ai/v1` | API base URL |
| `DEFAULT_MODEL` | `gpt-4o-mini` | Model to use |
| `DEFAULT_TEMPERATURE` | `0.0` | Output randomness |
| `MAX_TOKENS` | `200` | Max response length |

## Project Structure

```
natural-cli/
├── app.py             # Gradio web UI
├── config.py          # Pydantic settings
├── main.py            # Typer CLI entry point
├── system_prompt.md   # LLM system prompt
└── pyproject.toml     # Project metadata & dependencies
```
