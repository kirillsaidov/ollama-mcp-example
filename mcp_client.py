# module mcp_client

# system
import os, sys
import json
import asyncio
import traceback

# libs
import ollama
from fastmcp import Client


async def main(model: str):
    print(f'Running with model={model}. Type "/quit" to exit.')
    
    # Connect to server via transport=sse.
    # The server exposes an HTTP endpoint that our client can talk to.
    async with Client("http://localhost:8050/sse") as client:
        history = [{
            'role': 'system',
            'content': 'You are a helpfull assistant. Use tools if possible to get the latest data.'
        }]
        mcp_tools = await client.list_tools()
        ollama_tools = []
        
        # List available tools provided by the MCP server.
        print('Available tools:')
        for tool in mcp_tools:
            print(f'\t- {tool.name}')
            print(f'\t  {tool.description.split("\n")[0]}')

        # Convert MCP tools to Ollama function calling format.
        # If you want to create MCP client from scratch for another LLM provider,
        # you will have to convert tools to the format it accepts.
        for tool in mcp_tools:
            ollama_tools.append({
                'type': 'function',
                'function': {
                    'name': tool.name,
                    'description': tool.description,
                    'parameters': tool.inputSchema
                }
            })

        # Chat
        while True:
            try:
                # Get user input
                user_input = input('>> ').strip()
                if user_input.startswith('/'):
                    break

                # Append history
                history.append({'role': 'user', 'content': user_input})

                # Generate response
                response = ollama.chat(model, messages=history, tools=ollama_tools)

                # Check if we need to make any functions calls to MCP server.
                if response.message.tool_calls:
                    for tool in response.message.tool_calls:
                        print(f'Calling {tool.function.name}')
                        print(f'\tWith params: {tool.function.arguments}')

                        # call function via MCP server
                        result = await client.call_tool(tool.function.name, tool.function.arguments)
                        
                        # append the results to history as role:tool
                        history.append({
                            'role': 'tool',
                            'content': json.dumps(result, indent=2) if isinstance(result, dict) else str(result),
                            'name': tool.function.name,
                        })

                    # run ollama again to get the final coherent response
                    response = ollama.chat(model, messages=history, tools=ollama_tools)

                # append ollama response
                history.append({
                    'role': 'assistant',
                    'content': response.message.content,
                })
                print(response.message.content)
            except:
                traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main(
        model='qwen3:4b-instruct'
    ))


