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
            result = await client.commands.run('stagehand', task='Click the IANA-managed Reserved Domains link.', url='https://www.iana.org/help/example-domains', extract_instruction='Return the visible heading.', command_timeout=180)
            print(result)
            Path('stagehand.png').write_bytes(await sb.files.read_bytes(result['screenshot_path']))
        finally:
            await client.aclose()
    finally:
        await sb.close()

asyncio.run(main())
