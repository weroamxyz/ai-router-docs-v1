# API Content Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the 接口文档 content in `new-api-docs-v1` with the 16 API reference pages from `ai-router-docs`, using fumadocs MDX format and matching the source navigation structure.

**Architecture:** Create 16 new flat `.mdx` files at `content/docs/zh/api/` (one per API format), convert MkDocs `!!!` admonitions to fumadocs `<Callout>` components via a Python script, then replace `api/index.mdx` with fumadocs `<Cards>` linking to the new flat files, and update `api/meta.json` to show only the source navigation. The existing nested `ai-model/` and `management/` directories are left untouched (only hidden from nav).

**Tech Stack:** Python 3 (stdlib only), fumadocs-ui `<Callout>` + `<Card>`/`<Cards>` components, lucide-react icons

---

## File Map

### New files to create (16)

| Source (`ai-router-docs/docs/api/`) | Target (`new-api-docs-v1/content/docs/zh/api/`) |
|-------------------------------------|--------------------------------------------------|
| `openai-chat.md` | `openai-chat.mdx` |
| `anthropic-chat.md` | `anthropic-chat.mdx` |
| `google-gemini-chat.md` | `google-gemini-chat.mdx` |
| `qwen-chat.md` | `qwen-chat.mdx` |
| `openai-embedding.md` | `openai-embedding.mdx` |
| `openai-realtime.md` | `openai-realtime.mdx` |
| `openai-image.md` | `openai-image.mdx` |
| `gemini-image.md` | `gemini-image.mdx` |
| `qwen-image.md` | `qwen-image.mdx` |
| `openai-audio.md` | `openai-audio.mdx` |
| `veo-video.md` | `veo-video.mdx` |
| `veo-image-to-video.md` | `veo-image-to-video.mdx` |
| `wan-video.md` | `wan-video.mdx` |
| `wan-image-to-video.md` | `wan-image-to-video.mdx` |
| `wan-video-to-video.md` | `wan-video-to-video.mdx` |
| `seedance-2-video.md` | `seedance-2-video.mdx` |

### Files to modify (2)

- `content/docs/zh/api/index.mdx` — replace with fumadocs Cards linking to the 16 new files
- `content/docs/zh/api/meta.json` — replace pages list with source nav structure

### Files NOT touched

- `content/docs/zh/api/ai-model/**` — all existing nested files kept
- `content/docs/zh/api/management/**` — all existing nested files kept
- All other `meta.json` files under `ai-model/` and `management/`

---

## Conversion Rules

| MkDocs syntax | MDX output |
|---------------|-----------|
| `!!! info "Title"\n    text` | `<Callout type="info" title="Title">text</Callout>` |
| `!!! info\n    text` (no title) | `<Callout type="info">text</Callout>` |
| `!!! warning "Title"\n    text` | `<Callout type="warn" title="Title">text</Callout>` |
| `!!! note "Title"\n    text` | `<Callout type="note" title="Title">text</Callout>` |
| `!!! tip "Title"\n    text` | `<Callout type="info" title="Title">text</Callout>` |
| `!!! example "Title"\n    text` | `<Callout type="info" title="Title">text</Callout>` |
| `!!! abstract "Title"\n    text` | `<Callout type="info" title="Title">text</Callout>` |
| `hide: footer` frontmatter | removed |

No image path fixes or link fixes needed for the 16 active API files.

---

## Task 1: Write the API migration script

**Files:**
- Create: `scripts/migrate-api.py`

- [ ] **Step 1: Create the script**

Write this exact content to `/home/liusz/cursor_rule/job/hotfix/superpower/new-api-docs-v1/scripts/migrate-api.py`:

```python
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
```

- [ ] **Step 2: Verify syntax**

```bash
python3 -c "import ast; ast.parse(open('/home/liusz/cursor_rule/job/hotfix/superpower/new-api-docs-v1/scripts/migrate-api.py').read()); print('syntax OK')"
```

Expected: `syntax OK`

---

## Task 2: Run the migration script

**Files:**
- Modify: 16 `.mdx` files in `content/docs/zh/api/`

- [ ] **Step 1: Run the script**

```bash
cd /home/liusz/cursor_rule/job/hotfix/superpower/new-api-docs-v1
python3 scripts/migrate-api.py
```

Expected output (all 16 lines with ✓, then `Done: 16 converted, 0 missing`):
```
  ✓  openai-chat.md  →  openai-chat.mdx
  ✓  anthropic-chat.md  →  anthropic-chat.mdx
  ✓  google-gemini-chat.md  →  google-gemini-chat.mdx
  ✓  qwen-chat.md  →  qwen-chat.mdx
  ✓  openai-embedding.md  →  openai-embedding.mdx
  ✓  openai-realtime.md  →  openai-realtime.mdx
  ✓  openai-image.md  →  openai-image.mdx
  ✓  gemini-image.md  →  gemini-image.mdx
  ✓  qwen-image.md  →  qwen-image.mdx
  ✓  openai-audio.md  →  openai-audio.mdx
  ✓  veo-video.md  →  veo-video.mdx
  ✓  veo-image-to-video.md  →  veo-image-to-video.mdx
  ✓  wan-video.md  →  wan-video.mdx
  ✓  wan-image-to-video.md  →  wan-image-to-video.mdx
  ✓  wan-video-to-video.md  →  wan-video-to-video.mdx
  ✓  seedance-2-video.md  →  seedance-2-video.mdx

Done: 16 converted, 0 missing
```

- [ ] **Step 2: Verify no `!!!` syntax remains**

```bash
grep -rn "^!!!" /home/liusz/cursor_rule/job/hotfix/superpower/new-api-docs-v1/content/docs/zh/api/*.mdx || echo "CLEAN"
```

Expected: `CLEAN`

- [ ] **Step 3: Verify Callout import in a file that has admonitions**

```bash
head -6 /home/liusz/cursor_rule/job/hotfix/superpower/new-api-docs-v1/content/docs/zh/api/openai-chat.mdx
```

Expected:
```
---
title: OpenAI 对话格式（Chat Completions）
---

import { Callout } from 'fumadocs-ui/components/callout';
```

- [ ] **Step 4: Verify a titled callout is correctly formed**

```bash
grep -A2 'Callout type="info" title=' /home/liusz/cursor_rule/job/hotfix/superpower/new-api-docs-v1/content/docs/zh/api/openai-chat.mdx | head -6
```

Expected: output contains `<Callout type="info" title="官方文档">` followed by content.

---

## Task 3: Update api/index.mdx

**Files:**
- Modify: `content/docs/zh/api/index.mdx`

- [ ] **Step 1: Replace the entire file**

Write this exact content to `/home/liusz/cursor_rule/job/hotfix/superpower/new-api-docs-v1/content/docs/zh/api/index.mdx`:

```mdx
---
title: 接口文档
description: AI 模型接口参考文档
---

import { Card, Cards } from 'fumadocs-ui/components/card';
import { MessageSquare, Database, Radio, Image, Headphones, Video } from 'lucide-react';

## 功能接口

<Cards>
  <Card
    icon={<MessageSquare />}
    title="聊天（Chat）"
    description="支持 OpenAI、Anthropic、Google Gemini、Qwen 多种对话格式。"
    href="/zh/docs/api/openai-chat"
  />
  <Card
    icon={<Database />}
    title="嵌入（Embeddings）"
    description="文本向量嵌入服务，OpenAI 格式。"
    href="/zh/docs/api/openai-embedding"
  />
  <Card
    icon={<Radio />}
    title="实时对话（Realtime）"
    description="支持流式实时对话，OpenAI 格式。"
    href="/zh/docs/api/openai-realtime"
  />
  <Card
    icon={<Image />}
    title="图像（Image）"
    description="AI 图像生成服务，支持 OpenAI、Gemini、Qwen 格式。"
    href="/zh/docs/api/openai-image"
  />
  <Card
    icon={<Headphones />}
    title="音频（Audio）"
    description="语音相关服务，OpenAI 格式。"
    href="/zh/docs/api/openai-audio"
  />
  <Card
    icon={<Video />}
    title="视频（Video）"
    description="AI 视频生成服务，支持 Veo、Wan、SeeDance 格式。"
    href="/zh/docs/api/veo-video"
  />
</Cards>
```

- [ ] **Step 2: Verify the file**

```bash
head -8 /home/liusz/cursor_rule/job/hotfix/superpower/new-api-docs-v1/content/docs/zh/api/index.mdx
```

Expected:
```
---
title: 接口文档
description: AI 模型接口参考文档
---

import { Card, Cards } from 'fumadocs-ui/components/card';
import { MessageSquare, Database, Radio, Image, Headphones, Video } from 'lucide-react';
```

---

## Task 4: Update api/meta.json

**Files:**
- Modify: `content/docs/zh/api/meta.json`

- [ ] **Step 1: Replace the file**

Write this exact content to `/home/liusz/cursor_rule/job/hotfix/superpower/new-api-docs-v1/content/docs/zh/api/meta.json`:

```json
{
  "title": "接口文档",
  "description": "New API 接口文档",
  "icon": "Code",
  "root": true,
  "pages": [
    "index",
    "---聊天（Chat）---",
    "openai-chat",
    "anthropic-chat",
    "google-gemini-chat",
    "qwen-chat",
    "---嵌入（Embeddings）---",
    "openai-embedding",
    "---实时对话（Realtime）---",
    "openai-realtime",
    "---图像（Image）---",
    "openai-image",
    "gemini-image",
    "qwen-image",
    "---音频（Audio）---",
    "openai-audio",
    "---视频（Video）---",
    "veo-video",
    "veo-image-to-video",
    "wan-video",
    "wan-image-to-video",
    "wan-video-to-video",
    "seedance-2-video"
  ]
}
```

- [ ] **Step 2: Verify the file**

```bash
cat /home/liusz/cursor_rule/job/hotfix/superpower/new-api-docs-v1/content/docs/zh/api/meta.json
```

Expected: the JSON above, exactly as written.

---

## Task 5: Browser verification

- [ ] **Step 1: Navigate to the API index page**

Open: `http://192.168.28.131:3001/zh/docs/api`

Expected: Page titled "接口文档", shows 6 Cards: 聊天, 嵌入, 实时对话, 图像, 音频, 视频.

- [ ] **Step 2: Check the sidebar navigation**

Left sidebar under "接口文档" must show exactly these groups and items:
```
接口文档 (index)
聊天（Chat）
  OpenAI 对话格式（Chat Completions）
  Anthropic 格式（Messages）
  Google Gemini 格式（Generate Content）
  Qwen 格式（Text Generation）
嵌入（Embeddings）
  OpenAI 格式
实时对话（Realtime）
  OpenAI 格式
图像（Image）
  OpenAI 格式（Image）
  ...
音频（Audio）
  OpenAI 格式
视频（Video）
  Google Veo 文生视频...
  ...
```

No "管理接口", "AI 模型接口" sections visible in sidebar.

- [ ] **Step 3: Spot-check a content page with Callout**

Navigate to: `http://192.168.28.131:3001/zh/docs/api/openai-chat`

Expected: Page shows rendered Callout boxes (blue info box for "官方文档"), tables of models, curl request examples. No raw `!!!` text visible.

- [ ] **Step 4: Check nav tabs unchanged**

Top tabs must still show: **使用指南 | 接口文档 | 帮助支持 | 商务合作**
