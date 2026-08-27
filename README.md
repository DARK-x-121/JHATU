# JHATU

Terminal-based cybersecurity/OSINT assistant by **Amit** (Team Dark), powered by Groq's LLM API with a pluggable command layer.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # then fill in your keys
python main.py
```

## Features

- Password-gated terminal session (`SYSTEM_PASSWORD` in `.env`)
- Auto-fallback across multiple Groq models if one is unavailable
- Auto-loading plugin system — drop a `.py` file with a `run_plugin(user_input)` function into `plugins/` and it's picked up automatically
- Built-in Shodan recon plugin (`plugins/shodan_recon.py`) — passive lookups only, requires `SHODAN_API_KEY`
- Auto-saves generated code blocks to `~/JHATU_Projects/`
- `help`, `clear`, `exit` built-in commands

## Writing a plugin

```python
def run_plugin(user_input: str):
    if "your-trigger" in user_input.lower():
        return "your output string"
    return None  # returning None passes control to the next plugin / the AI model
```
