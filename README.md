# Ollama MCP for Dummies
This is a simple, beginner-friendly example showing how to set up and use an MCP server and client from scratch with Ollama. I assume you already know what MCP is conceptually.

## A summary of how MCP works
There are 3 components:
* **MCP server** - exposes your tools over a network.
* **MCP client** - connects to your MCP server and uses those tools.
* **LLM** - the language model that decides whether a tool is needed.

Basically, the MCP client is a wrapper for all tools. It connects to MCP servers and pulls their tools into a single list, exposing them to your language model as function calls.

Here is the schema:
```sh
┌─────────────┐         ┌─────────────┐         ┌──────────────┐
│   Ollama    │ <-----> │ MCP Client  │ <-----> │  MCP Server  │
│   (LLM)     │         │  (Wrapper)  │   SSE   │   (Tools)    │
└─────────────┘         └─────────────┘         └──────────────┘
                               │
                         Unifies tools
                         from multiple
                         MCP servers
```
The difference from regular function calling is that you don’t need to implement, define, or execute the tools yourself. MCP servers handle that. Most importantly, they are reusable and model-agnostic. _"Create once, then reuse."_

## What this example does
This project demonstrates how to set up and use MCP from scratch, showing what happens on both sides of the client and server under the hood:
1. Create MCP server. Expose tools over network. 
2. Create MCP client. Connect to MCP server and query for tools.
3. Handle chat and tool calls with Ollama.

## Quick start

### Prerequisites
- Python 3.8+
- Ollama installed and running
- The `qwen3:4b-instruct` model (or modify the code for your preferred model)

### Installation
#### Clone repo
```sh
git clone https://github.com/kirillsaidov/ollama-mcp-example.git
cd ollama-mcp-example
```
#### Install dependencies
```sh
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

#### Run the example
```sh
# start MCP server
./venv/bin/python mcp_server.py

# run MCP client
./venv/bin/python mcp_client.py
```

### Try it out
```sh
>> What's Apple's stock price?
Apple's current stock price is $252.13 per share.

>> How much is Google trading for?
Alphabet Inc. (GOOGL) is currently trading at 247.14 per share.
```

This is the same as my previous (`ollama-function-calling`](https://github.com/kirillsaidov/ollama-function-calling.git) example. The results are identical, but conceptually we now use MCP, which is more flexible and easily extensible. There is no need to modify your main app code. 

## How it works
The MCP client is essentially a tool wrapper that:
1. Connects to one or more MCP servers.
2. Collects all available tools from these servers.
3. Translates tools into a format your LLM understands (for function calling).
4. Routes tool calls back to the appropriate server instead of executing them locally.

## This project structure

```sh
ollama-function-calling/
├── mcp_server.py         # Exposing tools
├── mcp_client.py         # Connect to MCP server, get list of tools, expose them to LLM
├── README.md             # This file
└── requirements.txt      # Dependencies
```

## Customizing for your own functions

Want to add your own functions? Just add it to [`mcp_server.py`](./mcp_server.py):

```py
@mcp.tool()
def get_weather(city: str) -> str:
    # Your implementation here
    return f"Sunny, 75°F in {city}"
```

That's it. Noww you can test it by running the client script. 

## LICENSE
Unlicense.
