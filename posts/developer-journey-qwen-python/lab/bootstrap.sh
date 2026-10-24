set -eu
cd /home/user/journey-qwen
case "$(uname -m)" in x86_64) arch=x64 ;; aarch64) arch=arm64 ;; *) exit 2 ;; esac
archive="node-v24.16.0-linux-${arch}.tar.xz"
curl -fsSL "https://nodejs.org/dist/v24.16.0/$archive" -o "$archive"
curl -fsSL https://nodejs.org/dist/v24.16.0/SHASUMS256.txt -o SHASUMS256.txt
awk -v name="$archive" '$2 == name {print}' SHASUMS256.txt > node.sha256
[ -s node.sha256 ]
sha256sum -c node.sha256
tar -xJf "$archive"
ln -s "node-v24.16.0-linux-${arch}" node
export PATH="/home/user/journey-qwen/node/bin:$PATH"
npm install --prefix /home/user/journey-qwen/qwen @qwen-code/qwen-code@0.23.0
python3 -m pip install --index-url https://pypi.org/simple --disable-pip-version-check --target /home/user/journey-qwen/python agent-sandbox-server==0.3.1a1
node --version
/home/user/journey-qwen/qwen/node_modules/.bin/qwen --version
