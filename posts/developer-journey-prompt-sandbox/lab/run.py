"""Create a fresh model-generated add sandbox, verify it, and clean exact owned IDs.

Requires abx 0.4.12, agent-sandbox-client==0.3.1a2 and httpx. Configure provider
and model credentials in the environment. Reports are local; .private contains
resource IDs and raw output and must not be included in a published report.
"""
import argparse
import asyncio
import json
import hashlib
from importlib.metadata import version
import os
from pathlib import Path
import re
import shlex
import signal
import subprocess
import sys
import time

PROMPT = "创建一个 Python 沙箱，提供 add 命令接收两个整数并返回相加结果"
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", type=Path, default=Path("prompt-experiment"))
parser.add_argument("--cli", default="abx")
parser.add_argument("--generation-timeout", type=int, default=1200)
a = parser.parse_args()
root = a.output.resolve()
if root.exists():
    parser.error("choose a new output directory; previous evidence will not be overwritten")
root.mkdir(parents=True)
private = root / ".private"
private.mkdir(mode=0o700)
generated = root / "generated"
generated.mkdir()
base = shlex.split(a.cli)
env = dict(os.environ)
env["ABX_QWEN_CODEGEN_TIMEOUT"] = str(a.generation_timeout)
state = {"sandboxes": [], "templates": []}
report = {"prompt": PROMPT, "model": env.get("ABX_LLM_MODEL"), "generation_timeout_seconds": a.generation_timeout, "build_timeout_seconds": 600}


def safe(text):
    for value in state["sandboxes"] + state["templates"]:
        text = text.replace(value, "<owned-resource>")
    for key, value in env.items():
        if any(part in key for part in ("TOKEN", "API_KEY", "SECRET", "ACCESS_KEY", "BASE_URL", "SANDBOX_DOMAIN")) and len(value) > 5:
            text = text.replace(value, "<redacted>")
    text = re.sub(r"(?i)[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", "<resource-id>", text)
    return re.sub(r"https://[^\s\"\\]+\.(?:aliyuncs\.com|agentrun\.net|e2b\.dev)[^\s\"\\]*", "<private-provider-url>", text)


def call(name, args, timeout=120):
    result = subprocess.run([*base, *args], env=env, capture_output=True, text=True, timeout=timeout)
    (private / (name + ".json")).write_text(json.dumps({"stdout": result.stdout, "stderr": result.stderr, "exit_code": result.returncode}))
    return result


exit_code = 1
try:
    version_result = call("cli-version", ["--version"])
    if version_result.returncode != 0:
        raise RuntimeError("CLI version probe failed")
    report["versions"] = {"cli": version_result.stdout.strip(), "client": version("agent-sandbox-client"), "python": sys.version.split()[0]}
    report["script_sha256"] = {name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in ["run.py", "verify.py"]}
    started = time.monotonic()
    command = [*base, "--json", "create", "--prompt", PROMPT, "--yes", "--detach", "--build", "steps", "--dir", str(generated), "--timeout", "900"]
    process = subprocess.Popen(command, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)
    try:
        stdout, stderr = process.communicate(timeout=a.generation_timeout + 900)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            stdout, stderr = process.communicate(timeout=15)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate()
    (private / "create.json").write_text(json.dumps({"stdout": stdout, "stderr": stderr, "exit_code": process.returncode}))
    state["templates"] = list(dict.fromkeys(re.findall(r"Template registration submitted:\s*([A-Za-z0-9_-]+)", stderr)))
    try:
        result = json.loads(stdout)
        if result.get("ID"):
            state["sandboxes"] = [result["ID"]]
    except (ValueError, AttributeError):
        pass
    (private / "owned.json").write_text(json.dumps(state))
    report["create"] = {"exit_code": process.returncode, "elapsed_seconds": round(time.monotonic() - started, 2), "stdout": safe(stdout), "stderr": safe(stderr)}
    if process.returncode != 0 or len(state["sandboxes"]) != 1 or len(state["templates"]) != 1:
        raise RuntimeError("create did not produce exactly one owned sandbox and template")
    directories = [p for p in generated.iterdir() if p.is_dir()]
    if len(directories) != 1:
        raise RuntimeError("expected exactly one fresh generated directory")
    report["generated_sha256"] = {name: hashlib.sha256((directories[0] / name).read_bytes()).hexdigest() for name in ["commands.py", "Dockerfile", "template.yaml", "README.md"]}
    verification = subprocess.run([sys.executable, str(Path(__file__).with_name("verify.py")), "--sandbox-id", state["sandboxes"][0], "--template-id", state["templates"][0], "--generated-dir", str(directories[0]), "--output", str(root / "verification"), "--cli", a.cli], env=env, capture_output=True, text=True, timeout=600)
    (private / "verification.log").write_text(verification.stdout + verification.stderr)
    report["verification"] = {"exit_code": verification.returncode, "output": safe(verification.stdout + verification.stderr)}
    exit_code = verification.returncode
except Exception as error:
    report["failure"] = {"type": type(error).__name__, "message": safe(str(error))}
finally:
    cleanup = []
    for sid in state["sandboxes"]:
        item = {"kind": "sandbox", "absent": False}
        try:
            item["delete_exit_code"] = call("kill", ["kill", sid]).returncode
            from agent_sandbox import ProviderSandbox
            from agent_sandbox.models.errors import SandboxNotFoundError
            try:
                asyncio.run(ProviderSandbox.get_info_by_id(sid))
            except SandboxNotFoundError:
                item["absent"] = True
                item["typed_readback"] = "SandboxNotFoundError"
        except Exception as error:
            item["failure_type"] = type(error).__name__
        cleanup.append(item)
    for tid in state["templates"]:
        item = {"kind": "template", "absent": False}
        try:
            item["delete_exit_code"] = call("delete-template", ["template", "delete", tid, "-y"]).returncode
            result = call("template-after-delete", ["--json", "template", "info", tid])
            item["absent"] = result.returncode != 0 and "TemplateNotFound" in result.stdout + result.stderr
        except Exception as error:
            item["failure_type"] = type(error).__name__
        cleanup.append(item)
    report["cleanup"] = cleanup
    report["passed"] = exit_code == 0 and all(item["absent"] for item in cleanup)
    (root / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"passed": report["passed"], "cleanup": cleanup, "report": str(root / "report.json")}, indent=2))
raise SystemExit(0 if report["passed"] else 1)
