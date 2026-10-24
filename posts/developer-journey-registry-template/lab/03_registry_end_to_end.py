#!/usr/bin/env python3
"""Reproduce the public python-hello cloud-steps journey with published tools.

Prerequisites: Python 3.10+, Git, abx 0.4.12, PyYAML==6.0.3,
agent-sandbox-client==0.3.1a2, and authorized Express credentials in environment.
This creates billable cloud resources. It deletes only the exact IDs it creates.
Example: python 03_registry_end_to_end.py --output ./registry-proof --source-ref main
The output directory must be new. Private recovery state is in an owner-only
system temporary directory printed at start; logs and result.json are sanitized.
"""

from __future__ import annotations
import argparse, ast, asyncio, hashlib, json, os, pty, re, select, shutil
import subprocess, sys, tempfile, time, uuid
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", type=Path, required=True)
parser.add_argument(
    "--source-ref", default="main", help="Public awesome-templates commit or branch"
)
parser.add_argument("--abx", default=shutil.which("abx"))
parser.add_argument("--build-timeout", type=int, default=900)
a = parser.parse_args()
if not a.abx:
    raise SystemExit("Install the published abx CLI first.")
a.output.mkdir(parents=True, exist_ok=False)
private = Path(tempfile.mkdtemp(prefix="abx-registry-journey-"))
private.chmod(0o700)
work = private / "source"
state = {"alias": "journey-registry-" + uuid.uuid4().hex[:12]}
events = []
checks = []
print("Private recovery directory:", private, flush=True)
secrets = [
    v
    for k, v in os.environ.items()
    if any(
        w in k.upper()
        for w in [
            "TOKEN",
            "PASSWORD",
            "SECRET",
            "API_KEY",
            "ACCESS_KEY",
            "DOMAIN",
            "BASE_URL",
        ]
    )
    and len(v) >= 6
]


def save_state():
    p = private / "owned.json"
    p.write_text(json.dumps(state, indent=2))
    p.chmod(0o600)


def redact(value):
    text = str(value).replace(str(private), "<private-workdir>")
    for secret in sorted(secrets, key=len, reverse=True):
        text = text.replace(secret, "<redacted>")
    for key in ["sandbox_id", "template_id", "server_url"]:
        if state.get(key):
            text = text.replace(state[key], "<" + key + ">")
    text = re.sub(r'https?://[^\s"\\]+', "<url>", text)
    text = re.sub(
        r"(?i)[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}",
        "<request-or-resource-id>",
        text,
    )
    text = re.sub(r"micro-sandbox-[A-Za-z0-9<>-]+", "<provider-function>", text)
    text = re.sub(
        r"(?m)^.*(?:fcSessionDetails|teamID|teamName|resourceGroupID|instanceID|requestId|sandboxDomain|accessToken).*$",
        "<private-metadata>",
        text,
    )
    return text


def record(name, args, proc):
    event = {
        "step": name,
        "command": redact(" ".join(map(str, args))),
        "exit_code": proc.returncode,
        "stdout": redact(proc.stdout),
        "stderr": redact(proc.stderr),
    }
    events.append(event)
    (a.output / "commands.json").write_text(json.dumps(events, indent=2))


def run(name, args, *, ok=True, timeout=120, cwd=None, store=None):
    proc = subprocess.run(
        list(map(str, args)), text=True, capture_output=True, cwd=cwd, timeout=timeout
    )
    if store:
        recovery = private / (store + "-response.json")
        recovery.write_text(
            json.dumps(
                {
                    "stdout": proc.stdout,
                    "stderr": proc.stderr,
                    "exit_code": proc.returncode,
                }
            )
        )
        recovery.chmod(0o600)
    if store and proc.returncode == 0:
        value = (
            json.loads(proc.stdout)["TemplateID"]
            if store == "template_id"
            else proc.stdout.strip()
        )
        if not value or "\n" in value:
            raise RuntimeError(
                "Unexpected resource identifier response; inspect private recovery state."
            )
        state[store] = value
        save_state()
    record(name, args, proc)
    if ok and proc.returncode:
        raise RuntimeError(
            f"{name}: exit {proc.returncode}; see sanitized commands.json"
        )
    return proc


def cli(name, args, **kwargs):
    return run(name, [a.abx, *args], **kwargs)


def check(name, condition):
    checks.append({"name": name, "passed": bool(condition)})
    (a.output / "checks.json").write_text(json.dumps(checks, indent=2))
    print(name, "PASS" if condition else "FAIL", flush=True)
    if not condition:
        raise AssertionError(name)


def json_cli(name, args):
    return json.loads(cli(name, args).stdout)


def terminal(sid):
    master, slave = pty.openpty()
    p = subprocess.Popen(
        [a.abx, "connect", sid],
        stdin=slave,
        stdout=slave,
        stderr=slave,
        start_new_session=True,
    )
    os.close(slave)
    output = b""
    started = time.monotonic()
    sent = False
    try:
        while time.monotonic() - started < 30:
            ready, _, _ = select.select([master], [], [], 1)
            if ready:
                try:
                    chunk = os.read(master, 65536)
                except OSError:
                    break
                if not chunk:
                    break
                output += chunk
            if not sent and time.monotonic() - started > 3:
                os.write(
                    master,
                    b'cd /tmp\nexport JOURNEY_PTY_FLAG=held\nprintf "PTY_CHECK_%s:%s:%s\\n" PASS "$PWD" "$JOURNEY_PTY_FLAG"\nexit\n',
                )
                sent = True
            if p.poll() is not None:
                break
    finally:
        if p.poll() is None:
            p.terminate()
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            p.kill()
            p.wait()
        os.close(master)
    text = output.decode(errors="replace")
    (a.output / "terminal.txt").write_text(redact(text))
    check(
        "real PTY preserves cwd and environment",
        p.returncode == 0 and "PTY_CHECK_PASS:/tmp:held" in text,
    )


async def application(sid):
    import httpx
    from agent_sandbox import ProviderSandbox

    sb = await ProviderSandbox.connect(sid)
    try:
        async with await sb.application_client(9000) as client:
            result = await client.commands.run("hello", name="Python")
            check(
                "documented ProviderSandbox.application_client",
                result == "Hello, Python!",
            )
        url = sb.network.get_url(9000)
        state["server_url"] = url
        save_state()
        responses = []
        # This exact tested Express application binding requires neither an application
        # Bearer nor extra gateway headers. Other bindings may differ; template-level
        # anonymity alone does not establish gateway authentication requirements.
        # Do not forward control-plane API keys to the application server.
        async with httpx.AsyncClient(timeout=30) as client:
            for path, body, status, expected in [
                ("/commands/hello", {"name": "Ada"}, 200, {"result": "Hello, Ada!"}),
                (
                    "/commands/run_script",
                    {"code": "print(21 * 2)"},
                    200,
                    {"result": "42\n"},
                ),
                ("/commands/run_script", {}, 400, None),
                ("/commands/unknown", {}, 404, None),
            ]:
                response = await client.post(url + path, json=body)
                value = response.json()
                responses.append(
                    {"path": path, "status": response.status_code, "body": value}
                )
                check(
                    "external POST " + path + " " + str(status),
                    response.status_code == status
                    and (expected is None or value == expected),
                )
            response = await client.get(url + "/commands")
            check(
                "discovery hides internal command",
                response.status_code == 200 and "_debug_info" not in response.text,
            )
            response = await client.get(url + "/hello/Ada")
            check(
                "custom GET route",
                response.status_code == 200
                and response.json() == {"greeting": "Hello, Ada!"},
            )
        (a.output / "http.json").write_text(redact(json.dumps(responses, indent=2)))
    finally:
        await sb.close()


failure = None
completed = False
interrupted = False
cleanup = {}
try:
    save_state()
    from importlib.metadata import PackageNotFoundError, version

    try:
        optional_host_server_version = version("agent-sandbox-server")
    except PackageNotFoundError:
        optional_host_server_version = None

    (a.output / "versions.json").write_text(
        json.dumps(
            {
                "python": sys.version.split()[0],
                "agent-sandbox-client": version("agent-sandbox-client"),
                "agent-sandbox-server": optional_host_server_version,
                "PyYAML": version("PyYAML"),
            },
            indent=2,
        )
    )
    run(
        "source clone",
        [
            "git",
            "clone",
            "--quiet",
            "--no-checkout",
            "https://github.com/Alibaba-Agent-Sandbox/awesome-templates.git",
            work,
        ],
        timeout=180,
    )
    run("source checkout", ["git", "-C", work, "checkout", "--quiet", a.source_ref])
    revision = run(
        "source revision", ["git", "-C", work, "rev-parse", "HEAD"]
    ).stdout.strip()
    (a.output / "source.json").write_text(
        json.dumps(
            {
                "repository": "https://github.com/Alibaba-Agent-Sandbox/awesome-templates",
                "revision": revision,
                "command_sha256": hashlib.sha256(
                    (work / "python-hello/commands.py").read_bytes()
                ).hexdigest(),
            },
            indent=2,
        )
    )
    cli("CLI version", ["--version"])
    run(
        "documented source preparation",
        [
            sys.executable,
            "scripts/prepare_steps.py",
            "python-hello",
            "--output",
            private / "prepared",
        ],
        cwd=work,
    )
    shutil.copyfile(
        private / "prepared/steps-provenance.json", a.output / "steps-provenance.json"
    )
    cli(
        "steps deployment",
        [
            "--json",
            "template",
            "deploy",
            private / "prepared",
            "--build",
            "steps",
            "--alias",
            state["alias"],
            "-y",
        ],
        store="template_id",
    )
    deadline = time.monotonic() + a.build_timeout
    attempt = 0
    while True:
        attempt += 1
        data = json_cli(
            "template readiness " + str(attempt),
            ["--json", "template", "info", state["template_id"]],
        )
        status = data["status"]
        status = ast.literal_eval(status) if isinstance(status, str) else status
        phase = str(status.get("state", "")).lower()
        if phase == "ready":
            break
        if phase not in ["building", "pending", "creating", "submitted"]:
            raise RuntimeError("Template build stopped: " + phase)
        if time.monotonic() >= deadline:
            raise TimeoutError("Template did not reach READY before deadline")
        time.sleep(10)
    check("template READY", True)
    cli(
        "sandbox create",
        ["create", state["template_id"], "--detach", "--timeout", "1200"],
        store="sandbox_id",
    )
    sid = state["sandbox_id"]
    info = json_cli("sandbox info", ["info", sid, "--format", "json"])
    check("native info JSON", isinstance(info, dict))
    result = cli("exec", ["exec", sid, "--", "python3", "-c", "print(6*7)"])
    check("exec output", "42" in result.stdout)
    for name, args in [
        ("capabilities", ["--json", "sandbox", "capabilities", sid]),
        ("commands", ["--json", "sandbox", "command", "list", sid]),
        ("hello", ["--json", "run", sid, "hello", "--arg", "name=Ada"]),
        (
            "inline code",
            [
                "--json",
                "run",
                sid,
                "run_script",
                "--json-args",
                '{"code":"print(21 * 2)"}',
            ],
        ),
    ]:
        value = json_cli(name, args)
        check(
            name,
            (
                value == {"result": "Hello, Ada!"}
                if name == "hello"
                else value == {"result": "42\n"}
                if name == "inline code"
                else bool(value)
            ),
        )
    for filename, content in [
        ("main.py", "print(6 * 7)\n"),
        ("test_main.py", "def test_answer():\n    assert 6 * 7 == 42\n"),
    ]:
        local = private / filename
        local.write_text(content)
        cli("upload " + filename, ["upload", sid, local, "/home/user/app/" + filename])
    check(
        "uploaded script",
        json_cli(
            "run uploaded script",
            ["--json", "run", sid, "run", "--arg", "file=main.py"],
        )
        == {"result": "42\n"},
    )
    check(
        "uploaded pytest",
        "1 passed"
        in cli(
            "run uploaded pytest",
            ["--json", "run", sid, "test", "--arg", "path=test_main.py"],
        ).stdout,
    )
    for name, args in [
        ("files list", ["list", "--path", "/home/user/app"]),
        ("files stat", ["stat", "--path", "/home/user/app/main.py"]),
        ("files search", ["search", "--path", "/home/user/app", "--pattern", "*.py"]),
    ]:
        command = args[0]
        cli(name, ["--json", "sandbox", "files", command, sid, *args[1:]])
        check(name, True)
    cli(
        "download", ["download", sid, "/home/user/app/main.py", private / "download.py"]
    )
    check(
        "file SHA256",
        (private / "main.py").read_bytes() == (private / "download.py").read_bytes(),
    )
    cli("mkdir", ["sandbox", "files", "mkdir", sid, "--path", "/home/user/app/proof"])
    cli(
        "move",
        [
            "sandbox",
            "files",
            "mv",
            sid,
            "--source",
            "/home/user/app/main.py",
            "--dest",
            "/home/user/app/proof/moved.py",
        ],
    )
    cli(
        "remove confirmed",
        [
            "sandbox",
            "files",
            "rm",
            sid,
            "--path",
            "/home/user/app/proof/moved.py",
            "-y",
        ],
    )
    check(
        "removed file absent",
        "is empty"
        in cli(
            "removed file readback",
            [
                "--json",
                "sandbox",
                "files",
                "list",
                sid,
                "--path",
                "/home/user/app/proof",
            ],
        ).stdout,
    )
    for operation in ["info", "metrics", "ports", "packages"]:
        cli("system " + operation, ["--json", "sandbox", "system", operation, sid])
        check("system " + operation, True)
    cli(
        "filtered environment",
        ["--json", "sandbox", "system", "env", sid, "--filter", "PATH,HOME"],
    )
    check("filtered environment", True)
    cli("background process", ["exec", "--background", sid, "--", "sleep", "77"])
    processes = json_cli("process list", ["--json", "sandbox", "process", "list", sid])
    owned = [p for p in processes if "sleep 77" in p["command"]]
    check("owned process discovered", len(owned) == 1)
    pid = str(owned[0]["pid"])
    cli("process info", ["--json", "sandbox", "process", "info", sid, pid])
    cli("process signal", ["sandbox", "process", "signal", sid, pid, "--signal", "15"])
    processes = json_cli(
        "process readback", ["--json", "sandbox", "process", "list", sid]
    )
    check("owned process stopped", all(str(p["pid"]) != pid for p in processes))
    terminal(sid)
    asyncio.run(application(sid))
    completed = True
except BaseException as exc:
    interrupted = isinstance(exc, KeyboardInterrupt)
    failure = redact(type(exc).__name__ + ": " + str(exc))
    print(failure, flush=True)
finally:
    for kind in ["sandbox", "template"]:
        rid = state.get(kind + "_id")
        if not rid:
            continue
        try:
            args = (
                ["kill", rid]
                if kind == "sandbox"
                else ["template", "delete", rid, "-y"]
            )
            deleted = cli("delete owned " + kind, args, ok=False)
            args = (
                ["info", rid]
                if kind == "sandbox"
                else ["--json", "template", "info", rid]
            )
            readback = cli("read back deleted " + kind, args, ok=False)
            message = (readback.stdout + readback.stderr).lower()
            absent = readback.returncode != 0 and (
                ("wasn't found" in message or "sandboxnotfound" in message)
                if kind == "sandbox"
                else "templatenotfound" in message
            )
            cleanup[kind] = {
                "delete_exit_code": deleted.returncode,
                "readback_exit_code": readback.returncode,
                "readback_reason": (
                    "SandboxNotFound" if kind == "sandbox" else "TemplateNotFound"
                )
                if absent
                else "unconfirmed",
                "absent": absent,
            }
        except Exception as exc:
            cleanup[kind] = {"absent": False, "error": redact(str(exc))}
    passed = (
        completed
        and failure is None
        and bool(cleanup)
        and all(item["absent"] for item in cleanup.values())
    )
    result = {
        "passed": passed,
        "completed": completed,
        "checks": checks,
        "failure": failure,
        "cleanup": cleanup,
        "scope": "public Registry source prepared with its documented cloud-steps tool; Express only; no Docker build claim",
    }
    (a.output / "result.json").write_text(json.dumps(result, indent=2))
    print(
        json.dumps({"passed": passed, "checks": len(checks), "cleanup": cleanup}),
        flush=True,
    )
    raise SystemExit(0 if passed else 130 if interrupted else 1)
