# client_llm.py

import os
import json
import asyncio

from mcp import ClientSession                      # MCP client session
from mcp.client.sse import sse_client              # SSE transport helper
from langchain_google_genai import ChatGoogleGenerativeAI  # Gemini chat model

async def fetch_and_serialize_tools(sse_url: str, output_path: str):
    """
    Connect to the MCP server via SSE, list all tools, and serialize:
      - name
      - description
      - inputSchema
    into a JSON file at `output_path`.
    """
    async with sse_client(sse_url) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            tool_list = await session.list_tools()
            tools_info = {}

            for tool in tool_list.tools:
                tools_info[tool.name] = {
                    "description": tool.description,
                    "inputSchema": tool.inputSchema
                }

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(tools_info, f, indent=2, ensure_ascii=False)

            print(f"Serialized {len(tools_info)} tools to {output_path}")

async def main():
    # 1. Verify API key
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Set the GOOGLE_API_KEY environment variable")

    # 2. Initialize Gemini via LangChain
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=os.environ["GOOGLE_API_KEY"],
    )

    # 3. Quick sanity check with Gemini
    response = llm.invoke("Hello, Gemini! How’s your day?")
    print("Gemini response:", response.content)

    # 4. Fetch and write tool metadata
    SSE_URL = "http://localhost:8050/sse"
    OUTPUT_JSON = "tools.json"
    await fetch_and_serialize_tools(SSE_URL, OUTPUT_JSON)

if __name__ == "__main__":
    asyncio.run(main())
