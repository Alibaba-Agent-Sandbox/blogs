# Native Crush practical case

Result: PARTIAL

Date: 2026-10-27. Post template-practice-crush, actual native Crush0.98.1,
standalone CLI0.5.7/client-server0.4.0a6, Express default Docker source.
Owner evidence: https://github.com/Alibaba-Agent-Sandbox/awesome-templates/pull/255.

- Actual source repair preserved the original three tests and passed independent
  original/held-out checks; attached examples do not invent the model's repair text.
- Startup model qwen3.8-flash performed repair; separate qwen3.8-max instance
  completed fresh CLI/unchanged SDK/HTTP generation. Downloaded generated program
  independently prints Hello from the sandbox; all three reports were retrieved.
- Own sandbox/prepared template/images independently absent with zero uncertainty.
- Attached generated_hello.py, quickstart.py and report.txt are exact downloaded
  code/unchanged README SDK/original report bytes. The report's extension changes
  only for blog attachment publication; its content is unchanged.
- Validator initially rejected a GENERATED_REPORT.md attachment because only
  index language Markdown files are accepted. Renaming the attachment to report.txt
  resolved it: python scripts/validate.py PASS,15 posts/zero problems.
- Isolated website sync/build: PASS, both article routes and all three assets
  present. Configured-secret scan and diff checks: PASS. Current-head CI pending.

The earlier interpreter case merged in blogs PR19 as
531d3b2d7bc84348ace457b15c57c404d33a74c4. Source PR252 merged as
26f9cee590cffdd2b41c0b9845fa1d63e11b1a79. Interpreter full acceptance remains
blocked by exception replay Issue251; its article is not qualification evidence.

Attachment SHA256:
- generated_hello.py: bef5d52082fc48aa45a460aec4ec5d98605ef1d35735b4729ea07bb100595e03
- quickstart.py: ef9cb71021cfd490b299c464576d1d409003a1c74b8a39d1d5da589900cdb8c4
- report.txt: 17289fe41ff5baa8114adf7c0d84c3610f88947fd07e44be101873d4386e68e3
