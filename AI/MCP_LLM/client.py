# client.py
import asyncio                                    # Python async I/O :contentReference[oaicite:10]{index=10}
from mcp import ClientSession                     # High-level MCP client session :contentReference[oaicite:11]{index=11}
from mcp.client.sse import sse_client             # SSE transport helper :contentReference[oaicite:12]{index=12}
# from nest_asyncio import apply                  # Uncomment only for nested event loops

async def main():
    # 1. Establish SSE connection to the FastMCP server
    url = "http://localhost:8050/sse"             # Default SSE endpoint :contentReference[oaicite:13]{index=13}
    async with sse_client(url) as (read_stream, write_stream):
        # 2. Create and initialize MCP session
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()             # Perform JSON-RPC init

            # 3. Discover available tools
            tools_result = await session.list_tools()
            print("Available tools:")
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description}")

            # 4. Invoke the 'add' tool
            call_result = await session.call_tool(
                "add",
                arguments={"a": 2, "b": 3}
            )
            # Depending on SDK version, use .result or .content
            output = getattr(call_result, "result", None)
            if output is None:
                # Fallback to content list
                output = call_result.content[0].text
            print(f"2 + 3 = {output}")

if __name__ == "__main__":
    # For standalone scripts, plain asyncio.run is sufficient
    asyncio.run(main())
