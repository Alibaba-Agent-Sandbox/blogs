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
            await client.commands.run('scaffold', kind='next', path='preview-app')
            result = await client.commands.run('dev_start', kind='next', path='preview-app', timeout_s=120)
            print(result)
        finally:
            try:
                await client.commands.run('dev_stop')
            finally:
                await client.aclose()
    finally:
        await sb.close()

asyncio.run(main())
