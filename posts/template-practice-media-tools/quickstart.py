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
            await sb.files.write('/home/user/app/sample.wav', Path('sample.wav').read_bytes())
            result = await client.commands.run('transcode', input_path='sample.wav', output_name='sample.flac', preset='flac', max_seconds=5, command_timeout=60)
            print(result)
            Path('sample.flac').write_bytes(await sb.files.read_bytes(result['output_path']))
        finally:
            await client.aclose()
    finally:
        await sb.close()

asyncio.run(main())
