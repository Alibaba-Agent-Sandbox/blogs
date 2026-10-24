"""Verify the public CLI lifecycle and preserve evidence even after a failed check."""

import json
import subprocess
import time
from support import ROOT, PRIVATE, environment, redact

entries = []
sid = None
cleanup = workload = list_visible = False
failure = cleanup_error = None


def run(args, timeout=90):
    started = time.monotonic()
    p = subprocess.run(
        ["abx", *args],
        env=environment(),
        text=True,
        capture_output=True,
        timeout=timeout,
    )

    def clean(text):
        return redact(text).replace(sid, "<owned-sandbox>") if sid else redact(text)

    entries.append(
        {
            "command": "abx "
            + " ".join("<owned-sandbox>" if a == sid else a for a in args),
            "exit_code": p.returncode,
            "seconds": round(time.monotonic() - started, 2),
            "stdout": clean(p.stdout),
            "stderr": clean(p.stderr),
        }
    )
    return p


try:
    created = run(["create", "base", "--detach", "--timeout", "300"])
    assert created.returncode == 0, "create failed"
    sid = created.stdout.strip()
    assert sid and "\n" not in sid and " " not in sid, "unexpected create output"
    (PRIVATE / "sandbox-id").write_text(sid)
    entries[-1]["stdout"] = "<owned-sandbox>\n"
    assert run(["info", sid, "--format", "json"]).returncode == 0
    reply = run(["exec", sid, "--", "echo", "hello"])
    assert reply.returncode == 0 and reply.stdout.strip() == "hello"
    workload = True
    for delay in [0, 2, 5]:
        time.sleep(delay)
        listed = run(["list"])
        list_visible = listed.returncode == 0 and sid in listed.stdout
        if list_visible:
            break
    assert list_visible, "created sandbox did not become visible in list"
except Exception as error:
    failure = {"type": type(error).__name__, "message": redact(str(error))}
finally:
    if sid:
        try:
            assert run(["kill", sid]).returncode == 0, "kill failed"
            for delay in [0, 2, 5]:
                time.sleep(delay)
                info = run(["info", sid])
                cleanup = (
                    info.returncode != 0
                    and "wasn't found" in (info.stdout + info.stderr).lower()
                )
                if cleanup:
                    break
        except Exception as error:
            cleanup_error = {
                "type": type(error).__name__,
                "message": redact(str(error)),
            }
    result = {
        "status": (
            "PASS" if not failure and workload and list_visible and cleanup else "FAIL"
        ),
        "workload_pass": workload,
        "list_visibility_pass": list_visible,
        "cleanup_verified": cleanup,
        "failure": failure,
        "cleanup_error": cleanup_error,
        "commands": entries,
    }
    (ROOT / "evidence" / "result.json").write_text(
        redact(json.dumps(result, indent=2)) + "\n"
    )
    print(
        json.dumps({key: value for key, value in result.items() if key != "commands"})
    )
if result["status"] != "PASS":
    raise SystemExit(1)
