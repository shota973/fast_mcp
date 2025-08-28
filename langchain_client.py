# 参考　https://qiita.com/mkuwan/items/07a34f30f4926d09017a

from langchain_core.messages import SystemMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio
from langchain_ollama import ChatOllama
import json
from langgraph.prebuilt import create_react_agent
import model

llm = ChatOllama(
    model = model.CHAT_MODEL,
    temperature = 0,
    base_url = "http://localhost:11434"
)


def load_json_config(path=model.CONFIG_PATH):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
mcp_setting_config = load_json_config().get("mcpServers", {})
print(mcp_setting_config)


def print_messages(result):
    messages = result.get("messages", result)  # result["messages"] or result itself if already a list
    if not isinstance(messages, list):
        print("messagesがリストではありません")
        return
    for msg in messages:
        # クラス名またはtype属性で判定
        msg_type = msg.get("type") if isinstance(msg, dict) else type(msg).__name__
        if not msg_type and hasattr(msg, "__class__"):
            msg_type = msg.__class__.__name__
        print(f"\n--- {msg_type} ---")
        if isinstance(msg, dict):
            for k, v in msg.items():
                print(f"{k}: {v}")
        else:
            print(msg)
            
async def main():
    # クライアント生成（context manager を使わない）
    client = MultiServerMCPClient(mcp_setting_config)

    # MCPツール取得
    tools = await client.get_tools()

    sys_message = SystemMessage(
        content="あなたはMCPサーバーを使用するAIアシスタントです。"
                "Toolの結果を優先して回答として採用してください"
                "回答は日本語でお願いします。"
    )

    # エージェント作成
    agent = create_react_agent(llm, tools, prompt=sys_message)

    # クエリ送信
    result = await agent.ainvoke({"messages": "東京(Tokyo)の天気は？"})
    print_messages(result)

    # 必要なら明示的クローズ（実装されていれば）
    close = getattr(client, "close", None)
    if callable(close):
        await close()

if __name__ == "__main__":
    asyncio.run(main())