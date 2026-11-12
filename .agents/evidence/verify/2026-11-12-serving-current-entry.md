# Verification: current managed Agents serving entry

Date: 2026-11-12
Result: PARTIAL
Baseline: blogs main6c86ee3

## Scope

Update the managed-agents-one-endpoint deployment/setup/management instructions
to the current CLI while retaining original0.1.4 business results and assets.
No API client, artifact, cloud/model task or real acceptance receipt is changed.

## Executed checks

- `python scripts/validate.py`: 59 posts, zero problems.
- `python -m unittest discover -s scripts -p 'test_*.py'`: two passed.
- Template owner verified real catalog source acquisition, fresh pinned httpx
  venv, smoke-script help and CLI application preview without cloud changes.
- Shell/Python syntax, rendered routes/anchors and website integration results
  are recorded after the coordinated source sync.

## Delivery boundary

Current source instructions are not a claim that the historical Qwen case ran
again on the changed source. Template PR306 retains its existing LibreOffice
dependency gate; website integration must land through its owner workflow.

## Local syntax and provenance

27 Bash blocks and three Python blocks across the updated template READMEs and
article parsed successfully. Two README shell examples contain explicit revision
placeholders and were excluded from shell syntax checking. All historical case
programs/assets are byte-unchanged; only the article Markdown changed in posts/.

## Rendered integration

Website integration passed its18 docs/catalog tests, Astro check and1,337-page
build. Real Chrome checked the Registry template and website article in both
languages at390/1280 widths: eight content/navigation cases passed. All current
setup/deploy/delete snippets were visible, retired app commands and whole-catalog
clone were absent, HTTP-client headings and original case version attribution
were retained. Rendered106 blog pages had2,814 local route/fragment links with
zero failures. Local preview servers were shut down. The initial browser harness
used the incorrect website output directory and returned404; it was corrected
to the actual build output before these passing assertions. This does not
change or reclassify the previous separate strict favicon journey failure.
