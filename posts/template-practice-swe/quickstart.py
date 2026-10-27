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
            9000, token=os.environ["ABX_SERVER_TOKEN"], timeout=1200
        )
        try:
            prepared = await client.commands.run("swe_prepare")
            print(prepared)
            run_id = prepared["run_id"]
            try:
                print(await client.commands.run("swe_run_agent", run_id=run_id,
                    allow_execution=True, max_steps=30, command_timeout=600))
                report = await client.commands.run("swe_evaluate", run_id=run_id)
                print(report)
                Path("report.json").write_bytes(
                    await sb.files.read_bytes(report["report_path"]))
                Path("repair.patch").write_bytes(
                    await sb.files.read_bytes(report["patch_path"]))
            finally:
                await client.commands.run("swe_cleanup", run_id=run_id)
        finally:
            await client.aclose()
    finally:
        await sb.close()

asyncio.run(main())
