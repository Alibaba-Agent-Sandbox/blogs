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
            await client.commands.run('serve', entry='index.js', port=3000)
            result = await client.commands.run('request', path='/')
            print(result)
        finally:
            try:
                await client.commands.run('stop')
            finally:
                await client.aclose()
    finally:
        await sb.close()

asyncio.run(main())
