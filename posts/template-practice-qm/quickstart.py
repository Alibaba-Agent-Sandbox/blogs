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
            result = await client.commands.run('qm', prompt='Create hello.py in the current project. It must print Hello from QM. Run it and report the output.', command_timeout=300)
            print(result)
            Path('hello.py').write_bytes(await sb.files.read_bytes('/home/user/app/hello.py'))
        finally:
            await client.aclose()
    finally:
        await sb.close()

asyncio.run(main())
