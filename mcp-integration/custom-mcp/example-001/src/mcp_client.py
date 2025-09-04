import asyncio
import json

async def main():
    # Start the MCP server as subprocess
    server = await asyncio.create_subprocess_exec(
        "python", "src/mcp_server.py",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
    )

    async def send_request(request: dict):
        """Send JSON request and read one line response"""
        request_json = json.dumps(request).encode() + b"\n"
        server.stdin.write(request_json)
        await server.stdin.drain()
        response_line = await server.stdout.readline()
        return json.loads(response_line.decode())



    # Step 1: Initialize
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
            "roots": {
                "listChanged": True
            },
            "sampling": {},
            "elicitation": {}
            },
            "clientInfo": {
            "name": "ExampleClient",
            "title": "Example Client Display Name",
            "version": "1.0.0"
            }
        }
        }
    init_response = await send_request(init_request)
    print("Initialization Response:", init_response)

    # Step 2: Send "initialized" notification (no id, no response expected)
    initialized_notification = {
        "jsonrpc": "2.0",
        "method": "notifications/initialized",
        "params": {}
    }
    server.stdin.write(json.dumps(initialized_notification).encode() + b"\n")
    await server.stdin.drain()
    print("Sent 'initialized' notification")

    # Step 3: List tools
    list_tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    tools_response = await send_request(list_tools_request)
    print(f"Available Tools: {tools_response} \n")

    # Step 4: Call product_detail tool
    call_tool_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "product_detail",
            "arguments": {"product_id": "prd_001"}
        }
    }
    tool_response = await send_request(call_tool_request)
    print(f"Tool Response {tool_response} \n")

    # Clean up
    server.terminate()
    await server.wait()

if __name__ == "__main__":
    asyncio.run(main())
