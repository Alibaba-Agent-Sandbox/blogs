# Qwen Code sandbox case

Use Python 3.10+, public `agent-sandbox-client==0.4.0a2` and CLI 0.5.3. Configure the Express provider and your actual OpenAI-compatible model endpoint, then run `python lab/run.py` from the article directory. The developer host downloads exact official Node/Qwen archives, verifies their SHA256/SHA512 and uploads them through the SDK. The sandbox installs those local archives and the public server package. No pre-existing sandbox or tool installation is reused.

The example creates an authenticated application, calls its invoice command through Python/CLI/POST, asks the real Qwen model to edit calculator.py and create REPORT.md, runs four independent arithmetic checks and deletes its own sandbox. Optional Qwen extensions are omitted; only the headless model/file-tool path is covered.

`source-sha256-public-20261025-0.5.3.json` identifies the source actually used for the current public-release run. Older manifests and proof directories preserve their original runs and versions. Local `.private/` output must not be published. The current receipt is in `../proof/public-20261025-cli-0.5.3-sdk-0.4.0a2/`.
