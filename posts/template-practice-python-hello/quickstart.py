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
            result = await client.commands.run('run_script', code='from pathlib import Path\nrows = [12.50, 18.80, 20.00]\ntotal = sum(rows)\nPath("summary.txt").write_text(f"total={total:.2f}\\n")\nprint(f"total={total:.2f}")')
            print(result)
            Path('summary.txt').write_bytes(await sb.files.read_bytes('/home/user/app/summary.txt'))
        finally:
            await client.aclose()
    finally:
        await sb.close()

asyncio.run(main())
