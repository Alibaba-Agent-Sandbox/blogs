"""Observe real HTTP, never stub a backend; only clean IDs created by this process."""

import asyncio, contextlib, io, json, os, runpy, sys, time, traceback
from pathlib import Path
from support import environment, redact, ROOT, PRIVATE

os.environ.update(environment())
import httpx

work = Path(__file__).resolve().parent
name = sys.argv[1]
events = []
owned = {}
secrets = []


def clean(text):
    text = redact(str(text))
    for value in sorted(secrets, key=len, reverse=True):
        text = text.replace(value, "<owned-sandbox>")
    return text


def observe(request, response):
    url = request.url
    event = {"method": request.method, "path": url.path, "status": response.status_code}
    if request.method == "POST" and url.path.rstrip("/").endswith("/sandboxes"):
        try:
            data = response.json()
            event["response_keys"] = (
                list(data) if isinstance(data, dict) else ["not-object"]
            )
            sid = (
                data.get("sandboxID")
                or data.get("sandboxId")
                or data.get("sandbox_id")
                or data.get("id")
            )
            if sid and response.is_success:
                sid = str(sid)
                secrets.append(sid)
                owned[sid] = {
                    "url": str(url).rstrip("/") + "/" + sid,
                    "headers": dict(request.headers),
                }
                (PRIVATE / (name + "-owned.json")).write_text(
                    json.dumps({"ids": list(owned)})
                )
                event["owned_created"] = True
        except Exception as exc:
            event["observe_error"] = type(exc).__name__
    events.append(event)


original_sync = httpx.Client.send
original_async = httpx.AsyncClient.send


def sync_send(self, request, *a, **kw):
    response = original_sync(self, request, *a, **kw)
    if request.url.path.rstrip("/").endswith("/sandboxes"):
        response.read()
    observe(request, response)
    return response


async def async_send(self, request, *a, **kw):
    response = await original_async(self, request, *a, **kw)
    if request.url.path.rstrip("/").endswith("/sandboxes"):
        await response.aread()
    observe(request, response)
    return response


httpx.Client.send = sync_send
httpx.AsyncClient.send = async_send
result = {"case": name, "source": sys.argv[2]}
start = time.time()
out = io.StringIO()
err = io.StringIO()
try:
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        runpy.run_path(str(work / sys.argv[2]), run_name="__main__")
    result["experiment_pass"] = True
except BaseException as exc:
    result["experiment_pass"] = False
    result["error"] = traceback.format_exc()
finally:
    httpx.Client.send = original_sync
    httpx.AsyncClient.send = original_async
    cleanup = []
    with httpx.Client(timeout=30) as client:
        for sid, info in owned.items():
            headers = {
                k: v
                for k, v in info["headers"].items()
                if k.lower() not in ["content-length", "content-type", "host"]
            }
            item = {
                "owned_id": "<owned-sandbox>",
                "decorator_delete_events": sum(
                    e["method"] == "DELETE"
                    and sid in e["path"]
                    and e["status"] in [200, 204, 404]
                    for e in events
                ),
            }
            try:
                response = client.get(info["url"], headers=headers)
                item["post_call_info_status"] = response.status_code
                if response.status_code != 404:
                    item["fallback_kill_status"] = client.delete(
                        info["url"], headers=headers
                    ).status_code
                    item["post_fallback_info_status"] = client.get(
                        info["url"], headers=headers
                    ).status_code
                item["confirmed_absent"] = (
                    item.get("post_fallback_info_status", item["post_call_info_status"])
                    == 404
                )
            except BaseException as exc:
                item["error"] = str(exc)
                item["confirmed_absent"] = False
            cleanup.append(item)
    result.update(
        stdout=out.getvalue(),
        stderr=err.getvalue(),
        events=events,
        cleanup=cleanup,
        owned_count=len(owned),
        elapsed_seconds=round(time.time() - start, 2),
    )
    target = ROOT / "evidence" / (name + ".json")
    target.parent.mkdir(exist_ok=True)
    text = clean(json.dumps(result, ensure_ascii=False, indent=2))
    target.write_text(text + "\n")
    print(text)

# A successful data assertion must not hide missing lifecycle evidence or leaked resources.
overall = (
    result["experiment_pass"]
    and len(owned) == 1
    and all(
        item.get("confirmed_absent")
        and item.get("decorator_delete_events") == 1
        and "fallback_kill_status" not in item
        for item in cleanup
    )
)
sys.exit(0 if overall else 1)
