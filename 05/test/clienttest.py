from claude_agent_sdk import ClaudeSDKClient
import anyio
import os
from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault("ANTHROPIC_BASE_URL", "https://api.kimi.com/coding/")
os.environ.setdefault("ANTHROPIC_MODEL", "kimi-k2.6")
os.environ.setdefault("ANTHROPIC_SMALL_FAST_MODEL", "kimi-k2.6")
os.environ.setdefault("ANTHROPIC_API_KEY", os.getenv("KIMI_API_KEY"))

async def main():
    async with ClaudeSDKClient() as client:
        await client.query("2+2=?")

        # Extract and print response
        async for msg in client.receive_response():
            print(msg)

anyio.run(main)