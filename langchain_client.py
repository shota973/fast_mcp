# 参考　https://qiita.com/mkuwan/items/07a34f30f4926d09017a

from langchain_core.messages import SystemMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio
from langchain_ollama import ChatOllama
import json
from langgraph.prebuilt import create_react_agent
import model

def load_json_config(path=model.CONFIG_PATH):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

mcp_setting_config = load_json_config().get("mcpServers", {})
print(mcp_setting_config)

def print_messages(result) -> list[list[str]]:
    messages = result.get("messages", result)
    if not isinstance(messages, list):
        print("messagesがリストではありません")
        return [["error", ""]]
    results = []
    for msg in messages:
        message = ""
        msg_type = msg.get("type") if isinstance(msg, dict) else type(msg).__name__
        if not msg_type and hasattr(msg, "__class__"):
            msg_type = msg.__class__.__name__
        print(f"\n--- {msg_type} ---")
        if isinstance(msg, dict):
            for k, v in msg.items():
                print(f"{k}: {v}")
                message += f"{k}: {v}\n"
        else:
            print(msg)
            message += str(msg) + "\n"
        results.append([msg_type, message])
    return results

async def create_client():
    llm = ChatOllama(
        model = model.CHAT_MODEL,
        temperature = 0,
        base_url = "http://localhost:11434"
    )
    client = MultiServerMCPClient(mcp_setting_config)
    tools = await client.get_tools()
    sys_message = SystemMessage(
        content="あなたはMCPサーバーを使用するAIアシスタントです。"
                "Toolの結果を優先して回答として採用してください"
                "回答は日本語でお願いします。"
    )
    agent = create_react_agent(llm, tools, prompt=sys_message)
    return agent

async def send_message(agent, message: str) -> list[list[str]]:
    # ReAct エージェントは messages の履歴形式を期待
    result = await agent.ainvoke({"messages": [("human", message)]})
    results = print_messages(result)
    return results

async def main():
    agent = await create_client()
    await send_message(agent, "東京(Tokyo)の天気は？")

if __name__ == "__main__":
    asyncio.run(main())