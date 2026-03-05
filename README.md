# Todoist MCP Server

An MCP (Model Context Protocol) server that provides access to the Todoist API, allowing AI assistants to interact with Todoist data.

## Features

- List and retrieve items from the Todoist API
- Async HTTP client with error handling
- Typed responses with Pydantic models

## Installation

### Using mpak (Recommended)

```bash
# Configure your API key
mpak config set @nimblebraininc/todoist api_key=your_api_key_here

# Run the server
mpak run @nimblebraininc/todoist
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/NimbleBrainInc/mcp-todoist.git
cd mcp-todoist

# Install dependencies with uv
uv sync

# Set your API key
export TODOIST_API_KEY=your_api_key_here

# Run the server
uv run python -m mcp_todoist.server
```

## Configuration

### Getting Your API Key

1. Go to https://app.todoist.com/app/settings/integrations/developer
2. Create a new API key
3. Copy the key

### Claude Desktop Configuration

Add to your `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "todoist": {
      "command": "mpak",
      "args": ["run", "@nimblebraininc/todoist"]
    }
  }
}
```

## Available Tools

| Tool | Description |
|------|-------------|
| `list_items` | List items from the API with optional limit |
| `get_item` | Get a single item by its ID |

## Development

```bash
# Install dev dependencies
uv sync --dev

# Run tests
uv run pytest tests/ -v

# Format code
uv run ruff format src/ tests/

# Lint
uv run ruff check src/ tests/

# Type check
uv run ty check src/

# Run all checks
make check
```

## License

MIT
