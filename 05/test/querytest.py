import anyio
from claude_agent_sdk import query, ClaudeAgentOptions
import os
from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault("ANTHROPIC_BASE_URL", "https://api.kimi.com/coding/")
os.environ.setdefault("ANTHROPIC_MODEL", "kimi-k2.6")
os.environ.setdefault("ANTHROPIC_SMALL_FAST_MODEL", "kimi-k2.6")
os.environ.setdefault("ANTHROPIC_API_KEY", os.getenv("KIMI_API_KEY"))

async def main():

    options = ClaudeAgentOptions(
        system_prompt="你是一个有帮助的助手",  #系统提示词
        max_turns=3, #循环次数
        allowed_tools=["Read", "Write", "Bash"], #允许使用的工具
        permission_mode='acceptEdits', #设置工具权限，允许不经过人类确认，直接进行文件编辑
        cwd="/Users/Admin/workspace/python/claude-agent-sdk-demo/claude-agent" #工作目录
    )

    async for message in query(prompt="在当前目录下，新建一个test.txt文件，然后写入12345", options=options):
        print(message)

anyio.run(main)