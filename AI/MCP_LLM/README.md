# 📄 README: MCP_LLM

## Overview

This project demonstrates a modular architecture that integrates a Large Language Model (LLM) with dynamic tool invocation using the Model Context Protocol (MCP). The system enables the LLM to autonomously select and execute tools based on user queries, facilitating seamless interaction between the LLM and external functionalities.

## Prerequisites

Before running the script, ensure the following:

* **Python Version**: Python 3.7 or higher.
* **Environment Variable**: Set the `GOOGLE_API_KEY` environment variable with your Google API key.
* **MCP Server**: An MCP server should be running and accessible at `http://localhost:8050/sse`.

## Installation

1. **Open folder in VS code**:
Just open this folder in VS code.



2. **Create a Virtual Environment** (Optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```



3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```



*Note*: Ensure that `requirements.txt` includes the necessary packages such as `mcp`, `langchain_google_genai`, and any others used in the script.

4. **Push API Keys**:
Open server.py and give Tavily API key in that code
and the push gemini API in terminal and then run the server.py
   ```bash
   $Env:GOOGLE_API_KEY = "Your Gemini API key"
   python server.py
   ```

## Usage

Run the script from the command line, providing your query as an argument:

```bash
python client_llm2.py "What is the sum of 123 and 456?"
```

# For checking if your API is working correctly and generating tools.json file, run client_llm.py

```bash
python client_llm.py 
```

## Contributor

Akshat Trivedi : https://github.com/upmanya1
