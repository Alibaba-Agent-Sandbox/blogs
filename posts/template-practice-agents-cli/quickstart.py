import asyncio
import os
import time
from pathlib import Path
import httpx
from agent_sandbox import ProviderSandbox

async def main():
    sb = await ProviderSandbox.connect(
        os.environ["SANDBOX_ID"], provider=os.environ["ABX_PROVIDER"]
    )
    try:
        endpoint, gateway_headers = await sb.network.resolve(9000)
        headers = dict(gateway_headers)
        occupied = {key.lower() for key in headers}
        token = os.environ["ABX_SERVER_TOKEN"]
        if "authorization" not in occupied:
            headers["Authorization"] = "Bearer " + token
        if "x-access-token" not in occupied:
            headers["X-Access-Token"] = token
        if {"authorization", "x-access-token"}.issubset(occupied):
            raise ValueError("Gateway occupies both application authentication headers")
        base = httpx.URL(endpoint)
        def url(path):
            return base.copy_with(path=base.path.rstrip("/") + path)
        async with httpx.AsyncClient(headers=headers, timeout=60) as http:
            adapter = os.environ.get("AGENTS_ADAPTER", "qwen-code")
            if adapter not in ("qwen-code", "codex"):
                raise ValueError("AGENTS_ADAPTER must be qwen-code or codex")
            if adapter == "codex":
                response = await http.post(url("/commands/agents_configure_codex"), json={})
                response.raise_for_status()
            response = await http.post(url("/v1/agents/sessions"), json={
                "adapter": adapter,
                "agent": {"model": os.environ["OPENAI_MODEL"]},
                "environment": {"type": "self_hosted",
                                "workspace_directory": "/home/user/workspace"},
            })
            response.raise_for_status()
            session = response.json()["id"]
            path = "/v1/agents/sessions/" + session
            response = await http.post(url(path + "/events"), json={
                "events": [{"type": "agent.session.input.message", "input": [
                    {"role": "user", "content": [{"type": "input_text", "text":
                     "Create generated_hello.py that prints exactly Hello from the sandbox, "
                     "and GENERATED_REPORT.md explaining the program. Preserve unrelated files."}]}]}]
            })
            response.raise_for_status()
            deadline = time.monotonic() + 420
            while time.monotonic() < deadline:
                response = await http.get(url(path))
                response.raise_for_status()
                state = response.json()
                if state.get("error") or state.get("status") == "failed":
                    raise RuntimeError("Agent session failed; inspect private diagnostics")
                response = await http.get(url(path + "/items"))
                response.raise_for_status()
                items = response.json()["data"]
                if state.get("status") == "idle" and items:
                    print(items)
                    Path("generated_hello.py").write_bytes(await sb.files.read_bytes("/home/user/workspace/generated_hello.py"))
                    Path("GENERATED_REPORT.md").write_bytes(await sb.files.read_bytes("/home/user/workspace/GENERATED_REPORT.md"))
                    break
                await asyncio.sleep(1)
            else:
                raise TimeoutError("Destroy your owned sandbox to stop the task")
    finally:
        await sb.close()

asyncio.run(main())
