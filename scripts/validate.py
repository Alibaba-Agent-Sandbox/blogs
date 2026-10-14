#!/usr/bin/env python3
"""Check every post under posts/ against the front matter rules in README.md.

    python scripts/validate.py

Exits 1 when a post breaks a rule. Needs PyYAML.
"""
from __future__ import annotations

import datetime as dt
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "posts"
CATEGORIES = {"case", "tutorial", "announcement", "engineering"}
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
TAG = SLUG
HANDLE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")
LANGS = ("zh", "en")
FRONT = re.compile(r"\A---\n(.*?)\n---\n", re.S)
LOCAL_REF = re.compile(r"\]\((\./[^)#\s]+)")
SECRET = re.compile(r"(sk-[A-Za-z0-9]{16,}|LTAI[A-Za-z0-9]{12,}|ghp_[A-Za-z0-9]{20,})")

errors: list[str] = []


def fail(where: Path, message: str) -> None:
    errors.append(f"{where.relative_to(ROOT)}: {message}")


def check_file(path: Path, slug: str) -> dict | None:
    text = path.read_text(encoding="utf-8")
    match = FRONT.match(text)
    if not match:
        fail(path, "starts without a --- front matter block")
        return None
    try:
        meta = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as error:
        fail(path, f"front matter is not valid YAML: {error}")
        return None
    for key in ("title", "summary", "date", "category", "tags", "authors"):
        if key not in meta:
            fail(path, f"missing `{key}`")
    if not isinstance(meta.get("title"), str) or not meta["title"].strip():
        fail(path, "`title` must be a non-empty string")
    summary = meta.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        fail(path, "`summary` must be a non-empty string")
    elif len(summary) > 300:
        fail(path, f"`summary` is {len(summary)} characters, keep it under 300")
    if not isinstance(meta.get("date"), (dt.date, dt.datetime)):
        fail(path, "`date` must look like 2026-10-14")
    if meta.get("category") not in CATEGORIES:
        fail(path, f"`category` must be one of {sorted(CATEGORIES)}")
    tags = meta.get("tags")
    if not isinstance(tags, list) or not tags or len(tags) > 5 or not all(isinstance(t, str) and TAG.match(t) for t in tags):
        fail(path, "`tags` must be 1 to 5 lowercase hyphenated words")
    authors = meta.get("authors")
    if not isinstance(authors, list) or not authors or not all(isinstance(a, str) and HANDLE.match(a) for a in authors):
        fail(path, "`authors` must list GitHub handles")
    for flag in ("featured", "draft"):
        if flag in meta and not isinstance(meta[flag], bool):
            fail(path, f"`{flag}` must be true or false")
    cover = meta.get("cover")
    if cover is not None and not (path.parent / str(cover)).is_file():
        fail(path, f"`cover` points to {cover}, which does not exist")
    body = text[match.end():]
    for ref in LOCAL_REF.findall(body):
        if not (path.parent / ref).exists():
            fail(path, f"links to {ref}, which does not exist")
    if SECRET.search(text):
        fail(path, "looks like it contains a real secret; use <YOUR_API_KEY>")
    return meta


def main() -> int:
    if not POSTS.is_dir():
        print("posts/ not found", file=sys.stderr)
        return 1
    count = 0
    for directory in sorted(p for p in POSTS.iterdir() if p.is_dir()):
        slug = directory.name
        if not SLUG.match(slug):
            fail(directory, "directory name must be kebab-case")
        files = {lang: directory / f"index.{lang}.md" for lang in LANGS}
        present = {lang: f for lang, f in files.items() if f.is_file()}
        if not present:
            fail(directory, "needs index.zh.md and/or index.en.md")
            continue
        metas = {lang: check_file(f, slug) for lang, f in present.items()}
        if len(metas) == 2 and all(metas.values()):
            zh, en = metas["zh"], metas["en"]
            for key in ("date", "category"):
                if zh.get(key) != en.get(key):
                    fail(files["en"], f"`{key}` differs from the Chinese version")
        stray = [p.name for p in directory.glob("*.md") if p.name not in {f.name for f in files.values()}]
        for name in stray:
            fail(directory / name, "unexpected Markdown file; posts are index.zh.md and index.en.md")
        count += 1
    for message in errors:
        print(f"error: {message}")
    print(f"{count} post(s) checked, {len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
