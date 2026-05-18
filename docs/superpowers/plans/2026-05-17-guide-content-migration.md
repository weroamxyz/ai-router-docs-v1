# Guide Content Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the 使用指南 content in `new-api-docs-v1` (Next.js/fumadocs) with the corresponding content from `ai-router-docs` (MkDocs), converting format as needed.

**Architecture:** Write a Python conversion script that reads 26 source `.md` files from `ai-router-docs/docs/guide/`, converts MkDocs syntax (admonitions, relative image paths) to fumadocs MDX syntax, and writes the result to the matching `.mdx` files in `new-api-docs-v1/content/docs/zh/guide/`. Navigation structure (`meta.json` files), `feature-guide/*`, and `wiki/*` are NOT touched.

**Tech Stack:** Python 3 (stdlib only), fumadocs-ui `<Callout>` component, Next.js static assets in `public/`

---

## File Map

| Source (`ai-router-docs/docs/guide/`) | Target (`new-api-docs-v1/content/docs/zh/guide/`) |
|---------------------------------------|--------------------------------------------------|
| `home.md` | `home.mdx` |
| `about.md` | `about.mdx` |
| `document.md` | `document.mdx` |
| `pricing.md` | `pricing.mdx` |
| `console/playground.md` | `console/playground.mdx` |
| `console/dashboard.md` | `console/dashboard.mdx` |
| `console/api-token.md` | `console/api-token.mdx` |
| `console/usage-log.md` | `console/usage-log.mdx` |
| `console/chat.md` | `console/chat.mdx` ⚠️ has `!!!` admonitions |
| `console/profile.md` | `console/profile.mdx` |
| `console/wallet.md` | `console/wallet.mdx` |
| `console/drawing-log.md` | `console/drawing-log.mdx` |
| `console/task-log.md` | `console/task-log.mdx` |
| `console/user-management.md` | `console/user-management.mdx` |
| `console/channel-management.md` | `console/channel-management.mdx` |
| `console/redeem-code-management.md` | `console/redeem-code-management.mdx` |
| `console/settings/system-settings.md` | `console/settings/system-settings.mdx` |
| `console/settings/model-settings.md` | `console/settings/model-settings.mdx` |
| `console/settings/rate-settings.md` | `console/settings/rate-settings.mdx` |
| `console/settings/rate-limit-settings.md` | `console/settings/rate-limit-settings.mdx` |
| `console/settings/dashboard-settings.md` | `console/settings/dashboard-settings.mdx` |
| `console/settings/chat-settings.md` | `console/settings/chat-settings.mdx` |
| `console/settings/drawing-settings.md` | `console/settings/drawing-settings.mdx` |
| `console/settings/operation-settings.md` | `console/settings/operation-settings.mdx` |
| `console/settings/payment-settings.md` | `console/settings/payment-settings.mdx` |
| `console/settings/other-settings.md` | `console/settings/other-settings.mdx` |

**Skipped:**
- `guide/index.md` — content is all commented-out placeholders; target `zh/index.mdx` already customized
- `feature-guide/*`, `wiki/*` — no source counterpart, keep unchanged
- `meta.json` files — navigation structure unchanged

**Images:** All 54 guide images already exist in `new-api-docs-v1/public/assets/guide/`. No copy needed.

---

## Conversion Rules

| MkDocs syntax | MDX output |
|---------------|-----------|
| `!!! info\n    text` | `<Callout type="info">text</Callout>` |
| `!!! warning\n    text` | `<Callout type="warn">text</Callout>` |
| `!!! success\n    text` | `<Callout type="info">text</Callout>` |
| `!!! note\n    text` | `<Callout type="note">text</Callout>` |
| `../../assets/guide/x.png` | `/assets/guide/x.png` |
| `../assets/guide/x.png` | `/assets/guide/x.png` |
| `../../../assets/guide/x.png` | `/assets/guide/x.png` |
| `hide: footer` frontmatter | removed |
| `../support/faq.md` link | `/zh/docs/support/faq` |

---

## Task 1: Write the conversion script

**Files:**
- Create: `scripts/migrate-guide.py`

- [ ] **Step 1: Create the script**

```python
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
```

Save to: `new-api-docs-v1/scripts/migrate-guide.py`

- [ ] **Step 2: Verify the script exists**

```bash
ls /home/liusz/cursor_rule/job/hotfix/superpower/new-api-docs-v1/scripts/migrate-guide.py
```

Expected: file listed with no error.

---

## Task 2: Dry-run on one file to verify conversion

**Files:**
- Test target: `content/docs/zh/guide/console/chat.mdx` (only file with `!!!` syntax — best test case)

- [ ] **Step 1: Run script on chat.md only (manual preview)**

```bash
cd /home/liusz/cursor_rule/job/hotfix/superpower
python3 - <<'EOF'
import sys
sys.path.insert(0, 'new-api-docs-v1/scripts')
# Inline the key functions from migrate-guide.py to preview chat.md output
import re
from pathlib import Path

src = Path("ai-router-docs/docs/guide/console/chat.md")
raw = src.read_text()

# strip frontmatter
def strip_fm(t):
    if t.startswith("---"):
        end = t.find("\n---", 3)
        if end != -1:
            return t[end+4:].lstrip("\n")
    return t

TYPE_MAP = {"info":"info","warning":"warn","success":"info","note":"note"}

def convert_adm(text):
    needs = False
    lines = text.split("\n"); out = []; i = 0
    while i < len(lines):
        m = re.match(r'^!!!\s+(\w+)', lines[i])
        if m:
            t = TYPE_MAP.get(m.group(1).lower(), "info"); needs = True; body = []; i += 1
            while i < len(lines) and (lines[i].startswith("    ") or lines[i] == ""):
                body.append(lines[i][4:] if lines[i].startswith("    ") else ""); i += 1
            b = "\n".join(body).strip()
            out += [f'<Callout type="{t}">', b, "</Callout>"] if b else [f'<Callout type="{t}" />']
        else:
            out.append(lines[i]); i += 1
    return "\n".join(out), needs

content = strip_fm(raw)
content, needs = convert_adm(content)
content = re.sub(r"(?:\.\.\/)+assets\/guide\/", "/assets/guide/", content)
print(content[:2000])
EOF
```

Expected: Output shows `<Callout type="info">`, `<Callout type="warn">`, image paths like `/assets/guide/import-chat-config.png`. No `!!!` syntax remaining in first 2000 chars.

- [ ] **Step 2: Confirm no `!!!` syntax in preview output**

The output from Step 1 must NOT contain any `!!!` lines. If it does, fix the `convert_admonitions` function in the script before proceeding.

---

## Task 3: Run the full migration

**Files:**
- Modify: all 26 `.mdx` files listed in the File Map above

- [ ] **Step 1: Run the migration script**

```bash
cd /home/liusz/cursor_rule/job/hotfix/superpower/new-api-docs-v1
python3 scripts/migrate-guide.py
```

Expected output:
```
  ✓  home.md  →  home.mdx
  ✓  about.md  →  about.mdx
  ✓  document.md  →  document.mdx
  ✓  pricing.md  →  pricing.mdx
  ✓  playground.md  →  playground.mdx
  ✓  dashboard.md  →  dashboard.mdx
  ✓  api-token.md  →  api-token.mdx
  ✓  usage-log.md  →  usage-log.mdx
  ✓  chat.md  →  chat.mdx
  ✓  profile.md  →  profile.mdx
  ✓  wallet.md  →  wallet.mdx
  ✓  drawing-log.md  →  drawing-log.mdx
  ✓  task-log.md  →  task-log.mdx
  ✓  user-management.md  →  user-management.mdx
  ✓  channel-management.md  →  channel-management.mdx
  ✓  redeem-code-management.md  →  redeem-code-management.mdx
  ✓  system-settings.md  →  system-settings.mdx
  ✓  model-settings.md  →  model-settings.mdx
  ✓  rate-settings.md  →  rate-settings.mdx
  ✓  rate-limit-settings.md  →  rate-limit-settings.mdx
  ✓  dashboard-settings.md  →  dashboard-settings.mdx
  ✓  chat-settings.md  →  chat-settings.mdx
  ✓  drawing-settings.md  →  drawing-settings.mdx
  ✓  operation-settings.md  →  operation-settings.mdx
  ✓  payment-settings.md  →  payment-settings.mdx
  ✓  other-settings.md  →  other-settings.mdx

Done: 26 converted, 0 missing
```

If any file shows `✗ MISSING`, check that the source path is correct and re-run.

- [ ] **Step 2: Verify no `!!!` admonition syntax remains in any converted file**

```bash
grep -r "^!!!" /home/liusz/cursor_rule/job/hotfix/superpower/new-api-docs-v1/content/docs/zh/guide/console/ || echo "CLEAN — no admonitions remaining"
```

Expected: `CLEAN — no admonitions remaining`

- [ ] **Step 3: Verify no broken relative image paths remain**

```bash
grep -r "\.\./assets/guide/" /home/liusz/cursor_rule/job/hotfix/superpower/new-api-docs-v1/content/docs/zh/guide/ || echo "CLEAN — all paths absolute"
```

Expected: `CLEAN — all paths absolute`

- [ ] **Step 4: Verify Callout import exists in chat.mdx**

```bash
head -5 /home/liusz/cursor_rule/job/hotfix/superpower/new-api-docs-v1/content/docs/zh/guide/console/chat.mdx
```

Expected output contains:
```
---
title: 聊天
---

import { Callout } from 'fumadocs-ui/components/callout';
```

---

## Task 4: Browser verification

- [ ] **Step 1: Navigate to the guide pages and spot-check 3 key pages**

Open these URLs in a browser:

1. `http://192.168.28.131:3001/zh/docs/guide/console/chat` — must show `<Callout>` rendered (blue info boxes, yellow warning boxes), and images loading from `/assets/guide/`
2. `http://192.168.28.131:3001/zh/docs/guide/console/channel-management` — must show the parameter override documentation with code blocks
3. `http://192.168.28.131:3001/zh/docs/guide/console/settings/rate-settings` — must show the rate system documentation with tables and calculation examples

- [ ] **Step 2: Verify images render (not broken)**

On any of the above pages, check that images are visible (not broken). The images reference `/assets/guide/*.png` which already exist in `public/assets/guide/`.

- [ ] **Step 3: Verify navigation tabs are unchanged**

Top navigation must still show exactly: 使用指南 | 接口文档 | 帮助支持 | 商务合作

- [ ] **Step 4: Verify sidebar shows console pages**

Under 使用指南, the sidebar must show: 数据看板, API令牌, 渠道, 聊天, 操练场, 使用日志, ... (same structure as before, content from source)

---

## Rollback

If anything goes wrong, the original target `.mdx` files can be restored from git (if committed) or the content is non-destructive (we're only overwriting `.mdx` content, not deleting files). The `meta.json` and structural files are never touched by this plan.
