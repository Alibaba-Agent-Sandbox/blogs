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
            result = await client.commands.run('browse', url='data:text/html,<title>Invoice</title><h1>Total: 51.30</h1>', action='extract')
            print(result)
        finally:
            await client.aclose()
    finally:
        await sb.close()

asyncio.run(main())
