import asyncio, os
from datetime import timedelta
from urllib.parse import urlsplit
from opensandbox import Sandbox as NativeSandbox
from opensandbox.config import ConnectionConfig
from code_interpreter import CodeInterpreter, SupportedLanguage
from agent_sandbox import ProviderSandbox

async def main():
    provider = "opensandbox"
    sb = await ProviderSandbox.create(provider=provider, template="opensandbox/code-interpreter:v1.1.0", timeout=600, cpu=2, memory=3072,
        provider_options={"entrypoint": "/opt/code-interpreter/code-interpreter.sh"},
        envs={"PYTHON_VERSION": "3.11", "JAVA_VERSION": "17", "NODE_VERSION": "20", "GO_VERSION": "1.24"},
        )
    sid = sb.id
    try:
        url = urlsplit(os.environ.get("ABX_OPENSANDBOX_BASE_URL", "http://127.0.0.1:8080"))
        config = ConnectionConfig(domain=url.netloc, protocol=url.scheme,
            api_key=os.environ.get("ABX_OPENSANDBOX_API_KEY"),
            use_server_proxy=True, request_timeout=timedelta(seconds=60))
        native = await NativeSandbox.connect(sid, connection_config=config)
        try:
            interpreter = await CodeInterpreter.create(sandbox=native, ready_timeout=timedelta(seconds=120))
            try:
                context = await interpreter.codes.create_context(SupportedLanguage.PYTHON)
                first = await interpreter.codes.run("value = 37\nvalue", context=context)
                print(first.result[0].text)  # 37
                second = await interpreter.codes.run("value + 5", context=context)
                print(second.result[0].text)  # 42
                await interpreter.codes.delete_context(context.id)
            finally:
                await interpreter.aclose()
        finally:
            await native.close()
    finally:
        try:
            await sb.kill()
        finally:
            await sb.close()

asyncio.run(main())
