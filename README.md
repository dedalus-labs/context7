# Context7 MCP Server (Python)

A Python MCP server for the [Context7 API](https://context7.com/), providing up-to-date library documentation. Built with the [Dedalus MCP framework](https://github.com/dedalus-labs/dedalus-mcp-python).

## Features

- **resolve_library_id** - Resolve a library name to its Context7 ID
- **get_library_docs** - Fetch documentation for a specific library

## Installation

```bash
# Clone the repository
git clone https://github.com/dedalus-labs/context7-mcp-python.git
cd context7-mcp-python

# Install dependencies with uv
uv sync
```

## Configuration

Create a `.env` file with your Context7 API key:

```bash
CONTEXT7_API_KEY=your_api_key_here
```

Get your API key from [Context7](https://context7.com/).

## Usage

### Running the Server

```bash
uv run python src/main.py
```

The server will start on `http://localhost:3012/mcp`.

### Testing with the Client

```bash
uv run python src/client.py
```

## Tools

### resolve_library_id

Resolve a general library name to a Context7-compatible library ID.

**Parameters:**
- `library_name` (required): Library name to search for (e.g., "react", "nextjs", "postgres")

**Returns:** Matching libraries with their Context7 IDs

### get_library_docs

Fetch up-to-date documentation for a library from Context7.

**Parameters:**
- `library_id` (required): Exact Context7 library ID (e.g., "/mongodb/docs", "/vercel/next.js")
- `topic` (optional): Focus on a specific topic within the library
- `tokens` (optional): Max tokens of documentation (default: 10000)

**Returns:** Library documentation content

## License

MIT
