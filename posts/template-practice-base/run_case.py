"""Upload a CSV job to a managed Express base and download its JSON result."""
import asyncio
from pathlib import Path
import secrets
import shlex

from agent_sandbox import ProviderSandbox


async def main():
    sb = await ProviderSandbox.create(
        provider="alicloud-express", template="base", timeout=180,
    )
    folder = "/tmp/expenses-" + secrets.token_hex(8)
    try:
        created = await sb.commands.run("mkdir -p " + shlex.quote(folder), timeout=30)
        if created.exit_code != 0:
            raise RuntimeError("Could not create the task directory")
        await sb.files.write(folder + "/expenses.csv", "amount\n12.50\n18.80\n20.00\n")
        await sb.files.write(
            folder + "/summarize.py",
            Path(__file__).with_name("summarize.py").read_text(),
        )
        result = await sb.commands.run(
            "python3 " + shlex.quote(folder + "/summarize.py"), timeout=30,
        )
        if result.exit_code != 0:
            raise RuntimeError("The expense script failed")
        data = await sb.files.read(folder + "/summary.json")
        Path("summary.json").write_text(data)
        print(data, end="")
    finally:
        try:
            await sb.kill()
        finally:
            await sb.close()


asyncio.run(main())
