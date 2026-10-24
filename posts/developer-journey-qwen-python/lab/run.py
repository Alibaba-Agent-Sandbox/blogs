"""Create a real Qwen sandbox with public SDK; use custom command via SDK, CLI, HTTP."""

import asyncio, hashlib, json, os, secrets, subprocess, time, traceback
from pathlib import Path
import httpx
from support import ROOT, PRIVATE, VALUES, environment, redact

os.environ.update(environment())
from agent_sandbox import ProviderSandbox

WORK = ROOT
records = []
sid = None
sb = None
server = None
cleaned = False
model = os.environ.get("QWEN_MODEL", "qwen3-coder-flash")
for required in ["OPENAI_API_KEY", "OPENAI_BASE_URL"]:
    if not os.environ.get(required):
        raise SystemExit(f"Missing required environment variable: {required}")
app_token = secrets.token_urlsafe(32)
VALUES["JOURNEY_APP_TOKEN"] = app_token


def record(name, result):
    records.append({"name": name, "result": result})
    print(name, flush=True)
    (ROOT / "evidence" / "02-progress.json").write_text(
        redact(json.dumps(records, ensure_ascii=False, indent=2))
    )


async def remote(command, timeout=240):
    result = await sb.commands.run(command, timeout=timeout)
    record(
        "remote",
        {
            "command": command,
            "exit_code": result.exit_code,
            "stdout": result.stdout[-2500:],
            "stderr": result.stderr[-1500:],
        },
    )
    assert result.exit_code == 0, "remote command failed"
    return result


async def cli(args):
    env = environment()
    env["ABX_SERVER_TOKEN"] = app_token
    p = await asyncio.create_subprocess_exec(
        "abx",
        *args,
        env=env,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, err = await asyncio.wait_for(p.communicate(), 90)
    record(
        "cli",
        {
            "args": args,
            "exit_code": p.returncode,
            "stdout": out.decode(),
            "stderr": err.decode(),
        },
    )
    return p.returncode, out.decode(), err.decode()


async def main():
    global sid, sb, server, cleaned
    status = "FAIL"
    try:
        record(
            "model-configuration",
            {"model": model, "selection": "QWEN_MODEL or qwen3-coder-flash default"},
        )

        def created(value):
            global sid
            sid = value
            (PRIVATE / "02-sandbox-id").write_text(value)

        sb = await ProviderSandbox.create(
            template="base",
            timeout=900,
            metadata={"journey": "developer-journey-20261024-02"},
            on_created=created,
        )
        sid = sb.id
        (PRIVATE / "02-sandbox-id").write_text(sid)
        record("created", {"sandbox": "<owned-sandbox>", "template": "base"})
        await remote("mkdir -p /home/user/journey-qwen/project")
        await sb.files.write(
            "/home/user/journey-qwen/bootstrap.sh", (WORK / "bootstrap.sh").read_text()
        )
        await sb.files.write(
            "/home/user/journey-qwen/commands.py", (WORK / "commands.py").read_text()
        )
        await remote("bash /home/user/journey-qwen/bootstrap.sh", timeout=300)
        await sb.files.write(
            "/home/user/journey-qwen/project/calculator.py",
            "def add(a, b):\n    return a - b\n",
        )
        env = {
            "OPENAI_API_KEY": VALUES["OPENAI_API_KEY"],
            "OPENAI_BASE_URL": VALUES["OPENAI_BASE_URL"],
            "OPENAI_MODEL": model,
            "PATH": "/home/user/journey-qwen/node/bin:/home/user/journey-qwen/qwen/node_modules/.bin:/usr/local/bin:/usr/bin:/bin",
            "PYTHONPATH": "/home/user/journey-qwen/python",
        }
        server = await sb.start_server(
            port=9008,
            command="python3 -m agent_sandbox.server serve --port 9008 --commands /home/user/journey-qwen/commands.py",
            token=app_token,
            env=env,
            timeout=60,
        )
        record("server-health", await server.health())
        version = await server.commands.run("qwen_version")
        record("qwen-version", version)
        assert "0.23.0" in str(version)
        expected = {"total": "51.30", "quantity": 3, "discount_percent": 10}
        answer = await server.commands.run(
            "invoice_total", unit_price="19.00", quantity=3, discount_percent=10
        )
        record("special-sdk", answer)
        assert answer == expected
        code, out, err = await cli(
            [
                "run",
                sid,
                "invoice_total",
                "--server-port",
                "9008",
                "--json-args",
                json.dumps(
                    {"unit_price": "19.00", "quantity": 3, "discount_percent": 10}
                ),
            ]
        )
        assert code == 0, "CLI named command failed"
        assert json.loads(out) == expected
        async with httpx.AsyncClient(timeout=30, follow_redirects=False) as http:
            response = await http.post(
                server.base_url.rstrip("/") + "/commands/invoice_total",
                headers=server.auth_headers(),
                json={"unit_price": "19.00", "quantity": 3, "discount_percent": 10},
            )
            record(
                "special-http-post",
                {"status": response.status_code, "body": response.json()},
            )
            assert response.status_code == 200 and response.json()["result"] == expected
            rejected = await http.post(
                server.base_url.rstrip("/") + "/commands/invoice_total",
                headers=server.auth_headers(),
                json={"quantity": 3},
            )
            record("special-http-invalid", {"status": rejected.status_code})
            assert rejected.status_code == 400
            for label in ["missing-application-token", "wrong-application-token"]:
                denied_headers = {
                    key: value
                    for key, value in server.auth_headers().items()
                    if key.lower() != "authorization"
                }
                if label == "wrong-application-token":
                    denied_headers["Authorization"] = (
                        "Bearer intentionally-invalid-application-token"
                    )
                denied = await http.post(
                    server.base_url.rstrip("/") + "/commands/invoice_total",
                    headers=denied_headers,
                    json={"unit_price": "19.00", "quantity": 3, "discount_percent": 10},
                )
                record(label, {"status": denied.status_code})
                assert denied.status_code == 401
        prompt = "Use your file tools to edit calculator.py on disk so add(a, b) returns their arithmetic sum. Keep the function name. Use your file tools to create REPORT.md on disk explaining the bug and your fix. Do not merely describe proposed changes in your response. Work only in this directory."
        (WORK / "model-prompt.generated.txt").write_text(prompt + "\n")
        model_server = await sb.application_client(9008, token=app_token, timeout=180)
        try:
            outcome = await model_server.commands.run(
                "repair_calculator", prompt=prompt
            )
            record("qwen-model-task", outcome)
            for filename in ["qwen.last.json", "qwen.last.stderr"]:
                (PRIVATE / filename).write_text(
                    await sb.files.read("/home/user/journey-qwen/project/" + filename)
                )
            assert outcome.get("exit_code") == 0 and outcome.get(
                "report_exists"
            ), "Qwen exited without producing the requested report"
        finally:
            await model_server.aclose()
        source = await sb.files.read("/home/user/journey-qwen/project/calculator.py")
        report = await sb.files.read("/home/user/journey-qwen/project/REPORT.md")
        (WORK / "calculator.generated.py").write_text(source)
        (WORK / "REPORT.generated.md").write_text(report)
        assert report.strip()
        await remote(
            "python3 -I -c \"from pathlib import Path; ns={}; exec(compile(Path('/home/user/journey-qwen/project/calculator.py').read_text(), 'calculator.py', 'exec'), ns); assert all(ns['add'](a,b)==a+b for a,b in [(2,3),(-4,9),(0,0),(123,456)]); print('four independent arithmetic cases passed')\""
        )
        record(
            "model-artifact-validation",
            {
                "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
                "report_nonempty": True,
                "heldout_cases": 4,
            },
        )
        status = "PASS"
    except Exception as e:
        record(
            "failure",
            {
                "type": type(e).__name__,
                "message": str(e),
                "traceback": traceback.format_exc(),
            },
        )
    finally:
        if server:
            try:
                await server.aclose()
            except Exception:
                pass
        if sb:
            try:
                await sb.kill()
                record("kill", {"requested": True})
            except Exception as e:
                record("kill-error", {"type": type(e).__name__, "message": str(e)})
        if sid:
            try:
                if not sb:
                    code, out, err = await cli(["kill", sid])
                    record("partial-create-cleanup", {"exit_code": code})
                for delay in [0, 2, 5]:
                    await asyncio.sleep(delay)
                    code, out, err = await cli(["info", sid])
                    cleaned = code != 0 and "wasn't found" in (out + err).lower()
                    if cleaned:
                        break
            except Exception as e:
                record(
                    "cleanup-verification-error",
                    {"type": type(e).__name__, "message": str(e)},
                )
        final = {
            "status": status if cleaned else "FAIL",
            "cleanup_verified": cleaned,
            "records": records,
        }
        (ROOT / "evidence" / "result.json").write_text(
            redact(json.dumps(final, ensure_ascii=False, indent=2)) + "\n"
        )
        print(json.dumps({"status": final["status"], "cleanup_verified": cleaned}))
        return final["status"] == "PASS"


if not asyncio.run(main()):
    raise SystemExit(1)
