# Verification: Agent API guide source links

Result: PASS for scoped content and source links.

- Based on Blogs draft head `11da313932f950f06ff832b4a34d592a4045ebb0` and the two selection-guide changes.
- `python scripts/validate.py`: 60 posts, 0 problems. `git diff --check` passed.
- GitHub contents API returned HTTP 200 for the six recipe directories at immutable revision `048db39f5a865b07343ede2a93393ceab7f2df31`. Both languages link to that inspected source; the text still describes the templates as under validation.
- Website's existing source sync imported both edited language files. Final topic publication and runtime verification remain independent.
