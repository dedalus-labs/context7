# Copyright (c) 2025 Dedalus Labs, Inc. and its contributors
# SPDX-License-Identifier: MIT

"""Sample MCP client for testing the Context7 MCP server."""

import asyncio

from dedalus_mcp import MCPClient


SERVER_URL = "http://localhost:3012/mcp"


async def main() -> None:
    client = await MCPClient.connect(SERVER_URL)

    # List tools
    result = await client.list_tools()
    print(f"\nAvailable tools ({len(result.tools)}):\n")
    for t in result.tools:
        print(f"  {t.name}")
        if t.description:
            print(f"    {t.description[:80]}...")
        print()

    # Test resolve_library_id
    print("--- resolve_library_id ---")
    resolve_results = await client.call_tool(
        "resolve_library_id",
        {"library_name": "react"},
    )
    print(resolve_results)
    print()

    # Test get_library_docs
    print("--- get_library_docs ---")
    docs_results = await client.call_tool(
        "get_library_docs",
        {"library_id": "/facebook/react", "topic": "hooks", "tokens": 5000},
    )
    print(str(docs_results)[:1000] + "..." if len(str(docs_results)) > 1000 else docs_results)

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
