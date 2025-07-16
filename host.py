import asyncio
import json
from openai import OpenAI
from fastmcp import Client
from fastmcp.client.transports import PythonStdioTransport, NodeStdioTransport
# OpenAIのクライアントの準備
client = OpenAI(
    base_url = 'http://localhost:11434/v1',
    api_key='ollama', # required, but unused
)

# サーバースクリプトのパス
MY_SERVER_SCRIPT = "server.py"
FILESYSTEM_SCRIPT = "servers/src/filesystem/dist/index.js"
FETCH_SCRIPT = "servers/src/fetch/src/mcp_server_fetch/server.py"

# MCPサーバからツールスキーマを取得
async def get_tools():
    my_server_transport = PythonStdioTransport(script_path=MY_SERVER_SCRIPT)
    async with Client(my_server_transport) as my_server_client:
        tools = await my_server_client.list_tools()
    filesystem_transport = NodeStdioTransport(script_path=FILESYSTEM_SCRIPT)
    async with Client(filesystem_transport) as filesystem_client:
        filesystem_tools = await filesystem_client.list_tools()
        tools.extend(filesystem_tools)
    fetch_transport = PythonStdioTransport(script_path=FETCH_SCRIPT)
    async with Client(fetch_transport) as fetch_client:
        fetch_tools = await fetch_client.list_tools()
        tools.extend(fetch_tools)
    return tools

# MCPサーバのツールを呼び出す
async def call_tool(tool_name, tool_args):
    my_server_transport = PythonStdioTransport(script_path=MY_SERVER_SCRIPT)
    async with Client(my_server_transport) as my_server_client:
        result = await my_server_client.call_tool(tool_name, tool_args)
        if result is not None:
            return result
    filesystem_transport = NodeStdioTransport(script_path=FILESYSTEM_SCRIPT)
    async with Client(filesystem_transport) as filesystem_client:
        result = await filesystem_client.call_tool(tool_name, tool_args)
        if result is not None:
            return result
    fetch_transport = PythonStdioTransport(script_path=FETCH_SCRIPT)
    async with Client(fetch_transport) as fetch_client:
        result = await fetch_client.call_tool(tool_name, tool_args)
        if result is not None:
            return result
    return None

def main():
    # メッセージリストの準備
    messages = [
        {"role": "user", "content": "Strawberryに含まれるrの数をLetter Counterツールを使って数えてください。"}
    ]    

    # ツールの準備
    tools = [
        {
            "type": "function",
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.inputSchema
        }
        for tool in asyncio.run(get_tools())
    ]
    print("ツール:", tools)

    # 推論の実行
    response = client.chat.completions.create(
        model="qwen3",
        messages=messages,
        tools=tools
    )
    print("応答:", response.choices[0].message)
    if response.choices[0].finish_reason == "tool_calls":
        # 関数呼び出し
        tool_calls = response.choices[0].message.tool_calls
        for tool_call in tool_calls:
            print("関数呼び出し:", tool_call)

            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            result = asyncio.run(call_tool(tool_name, tool_args))
            print("関数呼び出し結果:", result)
            # メッセージリストの準備
            messages.append(tool_call)
            messages.append({
                "type": "function_call_output",
                "call_id": tool_call.call_id,
                "output": str(result)
            })

        # 推論の実行
        response2 = client.chat.completions.create(
            model="qwen3",
            messages=messages,
            tools=tools,
        )
        print("応答:", response2.choices[0].message.content)        
    else:
        print("関数呼び出しが見つかりませんでした。")

if __name__ == "__main__":
    main()