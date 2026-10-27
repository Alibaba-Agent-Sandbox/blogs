import asyncio
import os
from pathlib import Path
from agent_sandbox import ProviderSandbox

async def main():
    sb = await ProviderSandbox.connect(
        os.environ["SANDBOX_ID"], provider=os.environ["ABX_PROVIDER"]
    )
    try:
        client = await sb.application_client(
            9000, token=os.environ["ABX_SERVER_TOKEN"], timeout=450
        )
        try:
            result = await client.commands.run('apply_patch', patch_text='*** Begin Patch\n*** Add File: hello.txt\n+Hello from a patch\n*** End Patch\n')
            print(result)
            Path('hello.txt').write_bytes(await sb.files.read_bytes('/home/user/app/hello.txt'))
        finally:
            await client.aclose()
    finally:
        await sb.close()

asyncio.run(main())
