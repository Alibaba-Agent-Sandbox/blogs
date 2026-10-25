# Run the current generated-application example

Use CLI 0.5.6 and public Python client 0.4.0a6. Set the provider/model configuration and `ABX_SERVER_TOKEN` shown in the article, then run `python run.py --output ./new-run --cli abx` with a new output directory. The runner generates fresh code, verifies it and deletes only its own sandbox/template.

The current public CLI 0.5.6 / SDK 0.4.0a6 run asks explicitly for integer parameters a and b. It passed 54 runtime assertions after a fresh managed Qwen installation and independently confirmed sandbox/template absence. Its receipts are in `../proof/public-20261025-cli-0.5.6-sdk-0.4.0a6/`; `generated-public-20261025-0.5.6/` contains the exact generated files, including the unchanged model README. The reviewed article explains host-token configuration.

The earlier public CLI 0.5.5 / SDK 0.4.0a6 repeat passed 54 runtime assertions after a fresh managed Qwen installation. Its dated receipts are in `../proof/public-20261025-cli-0.5.5-sdk-0.4.0a6/`; `generated-public-20261025-0.5.5/` preserves the actual generated files without editing the model README. Follow the reviewed article for configuration and calling instructions. `generated-public-20261025-0.5.3/` is an earlier immutable captured example with its original hashes and runtime proof. Other `generated*` directories retain earlier historical model outputs; they are not the current installation or deployment instructions. Their bytes are preserved as evidence.

The top-level `proof.json` and `assertions.json` are historical receipts with their own embedded tool/runtime versions. They are not current API examples. Current public-version receipts live in the article's dated `proof/` directory.
