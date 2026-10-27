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
            await client.commands.run('services_start')
            result = await client.commands.run('services_sql', sql='CREATE TABLE usage_demo (amount integer); INSERT INTO usage_demo VALUES (5130); SELECT sum(amount) AS total_cents FROM usage_demo;')
            print(result)
        finally:
            try:
                await client.commands.run('services_stop')
            finally:
                await client.aclose()
    finally:
        await sb.close()

asyncio.run(main())
