# Registry case reproduction

The current case uses the public OpenSandbox `python-hello` source launch with CLI 0.5.6 and Python 0.4.0a6. Manual CLI, SDK and HTTP steps are in `../index.zh.md`.

The executable reproduction lives with the templates it verifies: [public_launch_e2e.py](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/scripts/public_launch_e2e.py) and [public-template-launch.yml](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/.github/workflows/public-template-launch.yml). This avoids maintaining a second provider-specific runner in the blog. It uses a real Docker-backed OpenSandbox server, public Registry source, installed public tools and exact owned cleanup.

The `evidence/` directories preserve their historical versions and backend scopes. They are not evidence for this current release. A separate Express default source attempt with CLI 0.5.3 failed E7020 because Docker was missing on that host; switching this case to OpenSandbox does not turn that failure into an Express pass.
