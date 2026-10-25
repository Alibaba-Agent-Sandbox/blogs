set -eu
cd /home/user/journey-qwen
# Qwen Code 0.23.0 requires Node >=22; the managed base currently supplies Node20.
# run.py downloads and verifies these exact official archives on the developer host.
printf '\n[1/3] Verify uploaded archives and install Node.js 24.16.0\n'
timeout --kill-after=5s 30 bash -eu <<'NODE_INSTALL'
case "$(uname -m)" in x86_64) arch=x64 ;; aarch64) arch=arm64 ;; *) exit 2 ;; esac
sha256sum -c node.sha256
sha512sum -c qwen.sha512
tar -xJf "node-v24.16.0-linux-${arch}.tar.xz"
ln -s "node-v24.16.0-linux-${arch}" node
NODE_INSTALL
export PATH="/home/user/journey-qwen/node/bin:$PATH"
# This case uses headless file tools, not optional audio/clipboard/image/native-PTY addons.
printf '\n[2/3] Install verified Qwen Code 0.23.0 archive with npm\n'
timeout --kill-after=5s 90 npm install --omit=optional --loglevel=info --timing --registry=https://registry.npmjs.org --prefix /home/user/journey-qwen/qwen /home/user/journey-qwen/qwen-code-0.23.0.tgz
printf '\n[3/3] Install agent-sandbox-server 0.4.0a6 from official PyPI\n'
timeout --kill-after=5s 80 python3 -m pip install --index-url https://pypi.org/simple --disable-pip-version-check --timeout 15 --retries 1 --target /home/user/journey-qwen/python agent-sandbox-server==0.4.0a6
node --version
/home/user/journey-qwen/qwen/node_modules/.bin/qwen --version
