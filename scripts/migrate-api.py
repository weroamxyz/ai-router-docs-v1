#!/usr/bin/env python3
"""Migrate ai-router-docs API content → new-api-docs-v1 MDX format."""

import re
from pathlib import Path

SOURCE = Path("/home/liusz/cursor_rule/job/hotfix/superpower/ai-router-docs/docs/api")
TARGET = Path("/home/liusz/cursor_rule/job/hotfix/superpower/new-api-docs-v1/content/docs/zh/api")

FILES = [
    ("openai-chat.md", "openai-chat.mdx"),
    ("anthropic-chat.md", "anthropic-chat.mdx"),
    ("google-gemini-chat.md", "google-gemini-chat.mdx"),
    ("qwen-chat.md", "qwen-chat.mdx"),
    ("openai-embedding.md", "openai-embedding.mdx"),
    ("openai-realtime.md", "openai-realtime.mdx"),
    ("openai-image.md", "openai-image.mdx"),
    ("gemini-image.md", "gemini-image.mdx"),
    ("qwen-image.md", "qwen-image.mdx"),
    ("openai-audio.md", "openai-audio.mdx"),
    ("veo-video.md", "veo-video.mdx"),
    ("veo-image-to-video.md", "veo-image-to-video.mdx"),
    ("wan-video.md", "wan-video.mdx"),
    ("wan-image-to-video.md", "wan-image-to-video.mdx"),
    ("wan-video-to-video.md", "wan-video-to-video.mdx"),
    ("seedance-2-video.md", "seedance-2-video.mdx"),
]

ADMONITION_TYPE_MAP = {
    "info": "info",
    "warning": "warn",
    "warn": "warn",
    "note": "note",
    "tip": "info",
    "example": "info",
    "abstract": "info",
    "danger": "error",
    "success": "info",
}


def strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:].lstrip("\n")
    return text


def extract_title(text: str) -> str:
    m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else ""


def convert_admonitions(text: str) -> tuple[str, bool]:
    """Convert MkDocs !!! admonitions (with optional quoted titles) to <Callout>.

    Pattern: !!! type ["optional title"]
              indented body (4-space indent)
    Returns (converted_text, needs_callout_import).
    """
    needs_import = False
    lines = text.split("\n")
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r'^!!!\s+(\w+)(?:\s+"([^"]*)")?\s*$', line)
        if m:
            adm_type = ADMONITION_TYPE_MAP.get(m.group(1).lower(), "info")
            title = m.group(2)  # None if no title
            needs_import = True
            body_lines = []
            i += 1
            while i < len(lines) and (lines[i].startswith("    ") or lines[i] == ""):
                body_lines.append(lines[i][4:] if lines[i].startswith("    ") else "")
                i += 1
            body = "\n".join(body_lines).strip()
            title_attr = f' title="{title}"' if title else ""
            if body:
                out.append(f'<Callout type="{adm_type}"{title_attr}>')
                out.append(body)
                out.append("</Callout>")
            else:
                out.append(f'<Callout type="{adm_type}"{title_attr} />')
        else:
            out.append(line)
            i += 1
    return "\n".join(out), needs_import


def convert(src: Path, dst: Path) -> None:
    raw = src.read_text(encoding="utf-8")
    content = strip_frontmatter(raw)
    title = extract_title(content)
    content, needs_callout = convert_admonitions(content)

    fm = f"---\ntitle: {title}\n---\n\n" if title else "---\n---\n\n"
    imports = "import { Callout } from 'fumadocs-ui/components/callout';\n\n" if needs_callout else ""
    dst.write_text(fm + imports + content.lstrip("\n"), encoding="utf-8")
    print(f"  ✓  {src.name}  →  {dst.name}")


def main() -> None:
    ok = err = 0
    for src_rel, dst_rel in FILES:
        src = SOURCE / src_rel
        dst = TARGET / dst_rel
        if not src.exists():
            print(f"  ✗  MISSING: {src}")
            err += 1
            continue
        convert(src, dst)
        ok += 1
    print(f"\nDone: {ok} converted, {err} missing")


if __name__ == "__main__":
    main()
