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
            9000, token=os.environ["ABX_SERVER_TOKEN"], timeout=750
        )
        try:
            result = await client.commands.run('appworld_run', max_steps=30, command_timeout=600)
            print(result)
            Path('appworld-result.zip').write_bytes(await sb.files.read_bytes(result['artifact_path']))
        finally:
            await client.aclose()
    finally:
        await sb.close()

asyncio.run(main())
