# Copyright (c) 2025 Dedalus Labs, Inc. and its contributors
# SPDX-License-Identifier: MIT

"""Context7 Library Documentation operations for MCP server.

Optional environment variables:
    CONTEXT7_API_KEY: Context7 API key (optional, for higher rate limits)

API Documentation:
    https://context7.com
"""

import os
from typing import Any

import httpx
from dotenv import load_dotenv
from pydantic import BaseModel

from dedalus_mcp import tool


load_dotenv()

# Read API key from environment (optional)
CONTEXT7_API_KEY = os.getenv("CONTEXT7_API_KEY", "")
CONTEXT7_BASE_URL = "https://context7.com/api"


# --- Response Models ---------------------------------------------------------


class Context7Result(BaseModel):
    """Generic Context7 API result."""

    success: bool
    data: Any = None
    error: str | None = None


# --- Helper ------------------------------------------------------------------


def _get_headers() -> dict[str, str]:
    """Get headers for Context7 API requests."""
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    if CONTEXT7_API_KEY:
        headers["X-Context7-Api-Key"] = CONTEXT7_API_KEY
    return headers


async def _request(path: str, params: dict[str, Any] | None = None) -> Context7Result:
    """Make a request to Context7 API.

    Args:
        path: API path
        params: Query parameters

    Returns:
        Context7Result with success status and data or error.
    """
    url = f"{CONTEXT7_BASE_URL}{path}"
    headers = _get_headers()

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params, timeout=60.0)
            
            if response.status_code == 429:
                return Context7Result(success=False, error="Rate limited. Please try again later.")
            if response.status_code == 401:
                return Context7Result(success=False, error="Unauthorized. Please check your API key.")
            if response.status_code == 404:
                return Context7Result(success=False, error="Library not found.")
            
            response.raise_for_status()
            
            # Check if response is JSON or text
            content_type = response.headers.get("content-type", "")
            if "application/json" in content_type:
                return Context7Result(success=True, data=response.json())
            else:
                return Context7Result(success=True, data=response.text)
    except Exception as e:
        return Context7Result(success=False, error=str(e))


# --- Context7 Tools ----------------------------------------------------------


@tool(
    description=(
        "Resolves a package/product name to a Context7-compatible library ID. "
        "You MUST call this before 'get_library_docs' to obtain a valid library ID "
        "UNLESS the user explicitly provides a library ID in the format '/org/project'. "
        "Returns matching libraries with name, description, code snippet counts, and trust scores."
    )
)
async def resolve_library_id(
    library_name: str,
) -> Context7Result:
    """Search for a library and get its Context7-compatible ID.

    Args:
        library_name: Library name to search for (e.g., 'react', 'nextjs', 'langchain').

    Returns:
        Context7Result with matching libraries and their IDs.
    """
    result = await _request("/v1/search", params={"query": library_name})
    
    if result.success and result.data:
        results = result.data.get("results", [])
        if not results:
            return Context7Result(
                success=True,
                data={"message": "No libraries found matching your query.", "results": []},
            )
        
        # Format results
        formatted = []
        for lib in results[:10]:  # Limit to top 10
            formatted.append({
                "library_id": lib.get("id", ""),
                "name": lib.get("name", ""),
                "description": lib.get("description", ""),
                "code_snippets": lib.get("codeSnippets", 0),
                "trust_score": lib.get("trustScore", 0),
                "versions": lib.get("versions", []),
            })
        
        result.data = {
            "message": f"Found {len(formatted)} matching libraries.",
            "results": formatted,
        }
    
    return result


@tool(
    description=(
        "Fetches up-to-date documentation for a library using its Context7-compatible library ID. "
        "You must call 'resolve_library_id' first to obtain the ID, UNLESS the user explicitly "
        "provides a library ID in the format '/org/project' or '/org/project/version'."
    )
)
async def get_library_docs(
    library_id: str,
    topic: str | None = None,
    tokens: int = 10000,
) -> Context7Result:
    """Fetch documentation for a library.

    Args:
        library_id: Context7-compatible library ID (e.g., '/mongodb/docs', '/vercel/next.js').
        topic: Optional topic to focus documentation on (e.g., 'hooks', 'routing').
        tokens: Maximum tokens of documentation to retrieve (default 10000).

    Returns:
        Context7Result with library documentation.
    """
    # Clean up library ID
    if library_id.startswith("/"):
        library_id = library_id[1:]
    
    params = {
        "tokens": max(tokens, 10000),  # Minimum 10000 tokens
        "type": "txt",
    }
    if topic:
        params["topic"] = topic
    
    result = await _request(f"/v1/{library_id}", params=params)
    
    if result.success:
        if not result.data or result.data in ["No content available", "No context data available"]:
            return Context7Result(
                success=False,
                error=(
                    "Documentation not found. This might happen because you used an invalid "
                    "library ID. Use 'resolve_library_id' to get a valid ID."
                ),
            )
        
        # Return documentation as data
        result.data = {
            "library_id": f"/{library_id}",
            "topic": topic,
            "documentation": result.data,
        }
    
    return result


# --- Export ------------------------------------------------------------------

context7_tools = [
    resolve_library_id,
    get_library_docs,
]
