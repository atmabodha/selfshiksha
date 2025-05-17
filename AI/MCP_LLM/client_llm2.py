# llm_client_call.py
import argparse
import asyncio
import json
import re
import os
import sys
from typing import Dict, Any

from mcp import ClientSession
from mcp.client.sse import sse_client
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

async def get_tools_directly(sse_url: str) -> Dict[str, Any]:
    """Fetch tools directly from MCP server"""
    async with sse_client(sse_url) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools_result = await session.list_tools()
            return {
                tool.name: {
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
                for tool in tools_result.tools
            }

async def call_tool(sse_url: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
    """Execute a tool through MCP server"""
    async with sse_client(sse_url) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments=arguments)
            return getattr(result, "result", None) or result.content[0].text

async def main(user_query: str):
    # 1. Connect to MCP server and get live tool information
    SSE_URL = "http://localhost:8050/sse"
    tools = await get_tools_directly(SSE_URL)
    
    # 2. Initialize Gemini LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=os.environ["GOOGLE_API_KEY"],
        temperature=0.1
    )

    # 3. Create dynamic tool selection prompt
    tools_list = []
    for name, details in tools.items():
        params = "\n".join([f"- {k}: {v}" for k, v in details['parameters']['properties'].items()])
        tools_list.append(
            f"Tool Name: {name}\n"
            f"Description: {details['description']}\n"
            f"Parameters:\n{params}\n"
        )

    prompt = f"""Analyze this query and select the appropriate tool. Respond ONLY with JSON containing:
- "tool": exact tool name (MUST be one of {list(tools.keys())})
- "arguments": parameter values matching the tool's requirements

Available Tools:
{"".join(tools_list)}

User Query: {user_query}

Response Format:
{{
  "tool": "tool_name",
  "arguments": {{
    "param1": value1,
    "param2": value2
  }}
}}"""

    # 4. Get tool selection from Gemini
    response = llm.invoke([HumanMessage(content=prompt)])
    raw_response = response.content.strip()
    
    # Clean JSON response
    json_str = re.sub(r'^```json|```$', '', raw_response, flags=re.IGNORECASE).strip()

    try:
        decision = json.loads(json_str)
        tool_name = decision["tool"]
        arguments = decision["arguments"]
    except (json.JSONDecodeError, KeyError) as e:
        raise ValueError(f"Failed to parse LLM response: {e}\nRaw response:\n{raw_response}") from e

    # 5. Validate tool selection
    if tool_name not in tools:
        raise ValueError(f"Invalid tool selected: {tool_name}. Valid options: {list(tools.keys())}")

    # 6. Execute the tool
    print(f"🔧 Executing {tool_name} with {arguments}")
    tool_result = await call_tool(SSE_URL, tool_name, arguments)

    # 7. Generate final answer with LLM
    answer_prompt = f"""Create a helpful answer using this data:
    
Original Question: {user_query}
Tool Used: {tool_name}
Tool Result: {tool_result}

Provide a concise, human-readable response:"""

    final_response = llm.invoke([HumanMessage(content=answer_prompt)])
    
    print("\n✅ Final Answer:")
    print(final_response.content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("query", type=str, help="User question to process")
    args = parser.parse_args()

    if not os.environ.get("GOOGLE_API_KEY"):
        raise RuntimeError("GOOGLE_API_KEY environment variable not set")

    asyncio.run(main(args.query))