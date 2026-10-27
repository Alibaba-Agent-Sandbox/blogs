import asyncio
import os
from agent_sandbox import ProviderSandbox

async def main():
    sb = await ProviderSandbox.connect(
        os.environ["SANDBOX_ID"], provider=os.environ["ABX_PROVIDER"]
    )
    try:
        await sb.commands.run("git -C /home/user/app init -q")
        client = await sb.application_client(
            9000, token=os.environ["ABX_SERVER_TOKEN"], timeout=420
        )
        try:
            print(await client.commands.run('aider', prompt='Create generated_hello.py that prints exactly Hello from the sandbox, and GENERATED_REPORT.md explaining the program. Preserve unrelated existing files.', files='["generated_hello.py","GENERATED_REPORT.md"]', allow_write=True, cwd='/home/user/app', command_timeout=300))
        finally:
            await client.aclose()
    finally:
        await sb.close()

asyncio.run(main())
