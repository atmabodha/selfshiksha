# server.py
import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP, Context
import requests
import re

# Load .env from project root
load_dotenv()

# API keys etc.
TAVILY_API_KEY="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"

# Create a single MCP server
mcp = FastMCP(
    name="UnifiedServer",
    host="0.0.0.0",
    port=8050,
    cors_allowed_origins=["*"],
)

# --- Web Search Tool ---
@mcp.tool()
async def web_search(ctx: Context, query: str, max_results: int = 5) -> dict:
    """Web search using Tavily API"""
    resp = requests.post(
        "https://api.tavily.com/search",
        json={"query": query, "api_key": TAVILY_API_KEY, "max_results": max_results},
        timeout=10,
    )
    return resp.json()

# --- RandomTools Suite ---
@mcp.tool()
def extract_dates(text: str) -> list[str]:
    return re.findall(r'\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4}', text)

@mcp.tool()
def validate_email(email: str) -> bool:
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

@mcp.tool()
def generate_slug(text: str) -> str:
    return re.sub(r'[^\w-]', '', text.strip().lower().replace(' ', '-'))[:60]

@mcp.tool()
def check_password_strength(password: str) -> bool:
    return len(password) >= 8 and any(c.isupper() for c in password) and any(c.isdigit() for c in password)

@mcp.tool()
def capitalize_names(name: str) -> str:
    return ' '.join(part.capitalize() for part in name.split())

@mcp.tool()
def extract_hashtags(text: str) -> list[str]:
    return re.findall(r'#\w+', text)

@mcp.tool()
def calculate_reading_time(text: str, wpm: int = 200) -> int:
    words = text.split()
    return max(1, round(len(words) / wpm))

@mcp.tool()
def basic_sentiment(text: str) -> int:
    POS, NEG = ['good','great','excellent','happy'], ['bad','poor','terrible','sad']
    words = set(text.lower().split())
    return sum(w in POS for w in words) - sum(w in NEG for w in words)

# --- Calculator Suite ---
@mcp.tool()
def add(a: int, b: int) -> int: return a + b
@mcp.tool()
def subtract(a: int, b: int) -> int: return a - b
@mcp.tool()
def multiply(a: int, b: int) -> int: return a * b
@mcp.tool()
def concatenate(s1: str, s2: str) -> str: return s1 + s2
@mcp.tool()
def is_even(n: int) -> bool: return n % 2 == 0
@mcp.tool()
def celsius_to_fahrenheit(c: float) -> float: return (c * 9/5) + 32
@mcp.tool()
def string_length(s: str) -> int: return len(s)
@mcp.tool()
def reverse_string(s: str) -> str: return s[::-1]

if __name__ == "__main__":
    import uvicorn
    print("Starting UnifiedServer on port 8050 (SSE transport)")
    uvicorn.run(mcp.sse_app(), host="0.0.0.0", port=8050)
