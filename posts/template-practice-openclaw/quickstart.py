import asyncio
import os
from agent_sandbox import ProviderSandbox

async def main():
    sb = await ProviderSandbox.connect(
        os.environ["SANDBOX_ID"], provider=os.environ["ABX_PROVIDER"]
    )
    try:
        client = await sb.application_client(
            9000, token=os.environ["ABX_SERVER_TOKEN"], timeout=420
        )
        try:
            print(await client.commands.run('gateway_start', bind='loopback', command_timeout=60))
            print(await client.commands.run("gateway_health"))
            first = await client.commands.run("gateway_chat", prompt="Summarize taxi 12.50, lunch 23.80 and train 15.00. Return only JSON with integer count and two-decimal string total.")
            print(first)
            print(await client.commands.run("gateway_chat", prompt="Remove the train from the previous expenses. Return the same JSON fields.", session_id=first["session_id"]))
        finally:
            try:
                await client.commands.run("gateway_stop")
            finally:
                await client.aclose()
    finally:
        await sb.close()

asyncio.run(main())
