"""Create a real Qwen sandbox with public SDK; use custom command via SDK, CLI, HTTP."""

import asyncio, base64, hashlib, json, os, secrets, subprocess, time, traceback
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
    partial_stdout, partial_stderr = [], []

    def output(chunk):
        partial_stdout.append(chunk)
        print(redact(chunk), end="", flush=True)

    def errors(chunk):
        partial_stderr.append(chunk)
        print(redact(chunk), end="", flush=True)

    try:
        result = await sb.commands.run(
            command, timeout=timeout, on_stdout=output, on_stderr=errors
        )
    except Exception:
        record("remote-failure", {
            "command": command,
            "partial_stdout": "".join(partial_stdout)[-12000:],
            "partial_stderr": "".join(partial_stderr)[-4000:],
        })
        raise
    record(
        "remote",
        {
            "command": command,
            "exit_code": result.exit_code,
            "stdout": result.stdout[-2500:],
            "stderr": result.stderr[-1500:],
        },
    )
    if result.exit_code != 0:
        try:
            names = sorted(
                Path(item.name).name for item in await sb.files.list("/home/user/.npm/_logs")
                if item.name.endswith("-debug-0.log")
            )
            if names:
                debug = await sb.files.read("/home/user/.npm/_logs/" + names[-1])
                target = PRIVATE / "npm-bootstrap-debug.log"
                target.write_text(debug)
                target.chmod(0o600)
                record("bootstrap-debug", {"private_log_saved": True})
        except Exception as error:
            record("bootstrap-debug", {"readback_error_type": type(error).__name__})
        raise AssertionError("remote command failed")
    return result


async def upload_official_tools():
    """Verify exact official archives on the developer host, then upload via SDK."""
    architecture = (await remote("uname -m")).stdout.strip()
    arch = {"x86_64": "x64", "aarch64": "arm64"}.get(architecture)
    if arch is None:
        raise RuntimeError(f"Unsupported sandbox architecture: {architecture}")
    node_archive = f"node-v24.16.0-linux-{arch}.tar.xz"
    node_origin = "https://nodejs.org/dist/v24.16.0/"
    qwen_url = "https://registry.npmjs.org/@qwen-code/qwen-code/-/qwen-code-0.23.0.tgz"
    qwen_integrity = "foznQtmptzM7DtYGPALZVtwUBVTsANYc6ytWOfGisXB7FgpzNmYT6xIHzh+26RJD9Kl+qzRW0gFp/AkqRouhnQ=="
    async with httpx.AsyncClient(timeout=180, follow_redirects=True) as http:
        async def fetch(url):
            response = await http.get(url)
            response.raise_for_status()
            return response.content
        node_bytes, checksums, qwen_bytes = await asyncio.gather(
            fetch(node_origin + node_archive),
            fetch(node_origin + "SHASUMS256.txt"),
            fetch(qwen_url),
        )
    expected = [line.split()[0] for line in checksums.decode().splitlines()
                if line.split()[-1] == node_archive]
    if len(expected) != 1 or hashlib.sha256(node_bytes).hexdigest() != expected[0]:
        raise AssertionError("Official Node.js archive checksum mismatch")
    if hashlib.sha512(qwen_bytes).digest() != base64.b64decode(qwen_integrity):
        raise AssertionError("Pinned official Qwen Code archive integrity mismatch")
    for name, content in [(node_archive, node_bytes),
                          ("node.sha256", f"{expected[0]}  {node_archive}\n"),
                          ("qwen-code-0.23.0.tgz", qwen_bytes),
                          ("qwen.sha512", f"{hashlib.sha512(qwen_bytes).hexdigest()}  qwen-code-0.23.0.tgz\n")]:
        await sb.files.write("/home/user/journey-qwen/" + name, content)
    record("official-tool-archives", {
        "node_version": "24.16.0", "node_architecture": arch,
        "node_bytes": len(node_bytes), "node_sha256": expected[0],
        "qwen_version": "0.23.0", "qwen_bytes": len(qwen_bytes),
        "qwen_integrity": "sha512-" + qwen_integrity,
        "delivery": "official host download, verified before SDK files.write",
    })


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
        await upload_official_tools()
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
                    if value not in {app_token, f"Bearer {app_token}"}
                }
                if label == "wrong-application-token":
                    denied_headers["Authorization"] = "Bearer intentionally-invalid-application-token"
                    denied_headers["X-Access-Token"] = "intentionally-invalid-application-token"
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
