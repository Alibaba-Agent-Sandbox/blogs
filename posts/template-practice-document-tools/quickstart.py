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
            await sb.files.write('/home/user/app/report.md', Path('report.md').read_bytes())
            result = await client.commands.run('convert', input_path='report.md', output_name='report.docx', output_format='docx')
            print(result)
            Path('report.docx').write_bytes(await sb.files.read_bytes(result['output_path']))
        finally:
            await client.aclose()
    finally:
        await sb.close()

asyncio.run(main())
