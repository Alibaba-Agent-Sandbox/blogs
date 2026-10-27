import asyncio
import os
from pathlib import Path
from agent_sandbox import ProviderSandbox

async def main():
    sb = await ProviderSandbox.connect(
        os.environ["ABX_SANDBOX_ID"], provider=os.environ["ABX_PROVIDER"]
    )
    try:
        await sb.commands.run("mkdir -p /home/user/workspace")
        client = await sb.application_client(
            9000, token=os.environ["ABX_SERVER_TOKEN"], timeout=660
        )
        try:
            result = await client.commands.run(
                "opencode_run",
                prompt="Create hello.py in the current directory that prints Hello from OpenCode, then run it.",
                model="dashscope/qwen3.8-flash",
                cwd="/home/user/workspace",
            )
            print(result["text"])
            Path("hello.py").write_bytes(
                await sb.files.read_bytes("/home/user/workspace/hello.py")
            )
        finally:
            await client.aclose()
    finally:
        await sb.close()

asyncio.run(main())
