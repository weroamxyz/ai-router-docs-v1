#!/usr/bin/env python3
"""Migrate ai-router-docs guide content → new-api-docs-v1 MDX format."""

import re
from pathlib import Path

SOURCE = Path("/home/liusz/cursor_rule/job/hotfix/superpower/ai-router-docs/docs/guide")
TARGET = Path("/home/liusz/cursor_rule/job/hotfix/superpower/new-api-docs-v1/content/docs/zh/guide")

FILES = [
    ("home.md", "home.mdx"),
    ("about.md", "about.mdx"),
    ("document.md", "document.mdx"),
    ("pricing.md", "pricing.mdx"),
    ("console/playground.md", "console/playground.mdx"),
    ("console/dashboard.md", "console/dashboard.mdx"),
    ("console/api-token.md", "console/api-token.mdx"),
    ("console/usage-log.md", "console/usage-log.mdx"),
    ("console/chat.md", "console/chat.mdx"),
    ("console/profile.md", "console/profile.mdx"),
    ("console/wallet.md", "console/wallet.mdx"),
    ("console/drawing-log.md", "console/drawing-log.mdx"),
    ("console/task-log.md", "console/task-log.mdx"),
    ("console/user-management.md", "console/user-management.mdx"),
    ("console/channel-management.md", "console/channel-management.mdx"),
    ("console/redeem-code-management.md", "console/redeem-code-management.mdx"),
    ("console/settings/system-settings.md", "console/settings/system-settings.mdx"),
    ("console/settings/model-settings.md", "console/settings/model-settings.mdx"),
    ("console/settings/rate-settings.md", "console/settings/rate-settings.mdx"),
    ("console/settings/rate-limit-settings.md", "console/settings/rate-limit-settings.mdx"),
    ("console/settings/dashboard-settings.md", "console/settings/dashboard-settings.mdx"),
    ("console/settings/chat-settings.md", "console/settings/chat-settings.mdx"),
    ("console/settings/drawing-settings.md", "console/settings/drawing-settings.mdx"),
    ("console/settings/operation-settings.md", "console/settings/operation-settings.mdx"),
    ("console/settings/payment-settings.md", "console/settings/payment-settings.mdx"),
    ("console/settings/other-settings.md", "console/settings/other-settings.mdx"),
]

ADMONITION_TYPE_MAP = {
    "info": "info",
    "warning": "warn",
    "warn": "warn",
    "success": "info",
    "note": "note",
    "tip": "info",
    "danger": "error",
}


def strip_frontmatter(text: str) -> str:
    """Remove YAML frontmatter block if present."""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:].lstrip("\n")
    return text


def extract_title(text: str) -> str:
    """Extract first H1 heading as the page title."""
    m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else ""


def convert_admonitions(text: str) -> tuple[str, bool]:
    """Convert MkDocs !!! admonitions to <Callout> components.

    Handles single-line and multi-line admonition bodies (4-space indent).
    Returns (converted_text, needs_callout_import).
    """
    needs_import = False
    lines = text.split("\n")
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r'^!!!\s+(\w+)(?:\s+"[^"]*")?\s*$', line)
        if m:
            adm_type = ADMONITION_TYPE_MAP.get(m.group(1).lower(), "info")
            needs_import = True
            # Collect indented body lines
            body_lines = []
            i += 1
            while i < len(lines) and (lines[i].startswith("    ") or lines[i] == ""):
                if lines[i].startswith("    "):
                    body_lines.append(lines[i][4:])
                else:
                    body_lines.append("")
                i += 1
            body = "\n".join(body_lines).strip()
            if body:
                out.append(f'<Callout type="{adm_type}">')
                out.append(body)
                out.append("</Callout>")
            else:
                out.append(f'<Callout type="{adm_type}" />')
        else:
            out.append(line)
            i += 1
    return "\n".join(out), needs_import


def fix_image_paths(text: str) -> str:
    """Convert relative ../../assets/guide/ paths to absolute /assets/guide/."""
    return re.sub(r"(?:\.\.\/)+assets\/guide\/", "/assets/guide/", text)


def fix_links(text: str) -> str:
    """Convert known relative .md links to absolute fumadocs paths."""
    text = text.replace("../support/faq.md", "/zh/docs/support/faq")
    return text


def convert(src: Path, dst: Path) -> None:
    raw = src.read_text(encoding="utf-8")
    content = strip_frontmatter(raw)
    title = extract_title(content)
    content, needs_callout = convert_admonitions(content)
    content = fix_image_paths(content)
    content = fix_links(content)

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
