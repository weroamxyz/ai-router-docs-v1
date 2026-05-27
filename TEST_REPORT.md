# API 接口文档测试报告

**测试时间**: 2026-05-22  
**测试地址**: https://computevault.unodetech.xyz  
**测试工具**: test_api.py（Python 脚本，见同目录）

---

## 一、整体结论

| 类别 | 文档模型总数 | 可用 | 不可用 | 文档问题 |
|------|------------|------|--------|---------|
| OpenAI Chat | 18 | 10 | 8 | 无 |
| Anthropic Chat | 5 | 5 | 0 | 无 |
| Gemini Chat | 14 | 4 | 10 | 无 |
| Qwen Chat | 3 | 3 | 0 | 无 |
| Embeddings | 1 | 1 | 0 | 无 |
| OpenAI Audio (TTS/STT/翻译) | 3 | 3 | 0 | 无 |
| OpenAI Image | 1 | 1 | 0 | **有（重复条目）** |
| Gemini Image | 2 | 2 | 0 | 无 |
| Qwen Image (生成) | 2 | 2 | 0 | **有（size 格式未说明）** |
| Qwen Image (编辑) | 3 | 2 | 0\* | **有（HTTP 200+错误体）** |
| Veo Video | 4 | 2 | 2 | 无 |
| Wan Video | 2 | 2 | 0 | **有（响应字段命名错误）** |
| SeeDance Video | 4 | 4 | 0 | **有（响应字段命名错误）** |
| Video 查询端点 | — | — | — | **有（状态值不一致）** |

> \* `wan2.5-i2i-preview` 功能正常但响应码设计不合理（HTTP 200 返回错误体）

---

## 二、需要修改文档的问题（按优先级排序）

---

### 问题 1：OpenAI Chat — 8 个模型无可用渠道，应从文档移除或标注

**文件**: `content/docs/en/api/openai-chat.mdx`  
**严重程度**: 高  

以下模型在支持模型列表中有记录，但实际调用均返回 `HTTP 503 分组 default 下模型 xxx 无可用渠道（distributor）`：

| 模型 | 文档现状 | 实际状态 |
|------|---------|---------|
| gpt-3.5-turbo-16k | 已记录 | ❌ 503 无渠道 |
| gpt-3.5-turbo-instruct | 已记录 | ❌ 503 无渠道 |
| gpt-4 | 已记录 | ❌ 503 无渠道 |
| gpt-4-32k | 已记录 | ❌ 503 无渠道 |
| gpt-4-turbo-preview | 已记录 | ❌ 503 无渠道 |
| gpt-4-turbo | 已记录 | ❌ 503 无渠道 |
| gpt-4-vision-preview | 已记录 | ❌ 503 无渠道 |
| gpt-4.5-preview | 已记录 | ❌ 503 无渠道 |

**可用的 OpenAI Chat 模型**（验证通过）：
`gpt-3.5-turbo`, `gpt-4o`, `gpt-4o-mini`, `gpt-4.1`, `gpt-4.1-mini`, `gpt-4.1-nano`, `gpt-5`, `gpt-5-chat-latest`, `gpt-5-mini`, `gpt-5-nano`

**建议修改**：从支持模型表中删除这 8 个无渠道的模型，或在表格中标注"暂不可用"。

---

### 问题 2：Gemini Chat — 10 个模型无可用渠道，应从文档移除或标注

**文件**: `content/docs/en/api/google-gemini-chat.mdx`  
**严重程度**: 高  

以下模型调用均返回 `HTTP 503 分组 default 下模型 xxx 无可用渠道（distributor）`：

| 模型 | 文档现状 | 实际状态 |
|------|---------|---------|
| gemini-1.5-pro | 已记录 | ❌ 503 无渠道 |
| gemini-1.5-flash | 已记录 | ❌ 503 无渠道 |
| gemini-1.5-flash-8b | 已记录 | ❌ 503 无渠道 |
| gemini-1.5-pro-latest | 已记录 | ❌ 503 无渠道 |
| gemini-1.5-flash-latest | 已记录 | ❌ 503 无渠道 |
| gemini-2.0-flash | 已记录 | ❌ 503 无渠道 |
| gemini-2.0-flash-lite-preview | 已记录 | ❌ 503 无渠道 |
| gemini-2.0-flash-exp | 已记录 | ❌ 503 无渠道 |
| gemini-2.0-pro-exp | 已记录 | ❌ 503 无渠道 |
| gemini-2.0-flash-thinking-exp | 已记录 | ❌ 503 无渠道 |

**可用的 Gemini Chat 模型**（验证通过）：
`gemini-2.5-flash`, `gemini-2.5-pro`, `gemini-3-pro-preview`, `gemini-3-flash-preview`

**建议修改**：从支持模型表中删除 10 个无渠道模型，仅保留实际可用的 4 个。

---

### 问题 3：Veo Video — 2 个模型无可用渠道

**文件**: `content/docs/en/api/veo-video.mdx`  
**严重程度**: 高  

| 模型 | 文档现状 | 实际状态 |
|------|---------|---------|
| veo-3.1-generate-001 | 已记录 | ❌ 503 无渠道 |
| veo-3.1-fast-generate-001 | 已记录 | ❌ 503 无渠道 |
| veo-3.0-generate-001 | 已记录 | ✅ 正常 |
| veo-3.0-fast-generate-001 | 已记录 | ✅ 正常 |

**建议修改**：从支持模型表中删除 `veo-3.1-*` 两个模型，或标注为"暂不可用"。

---

### 问题 4：OpenAI Image — 模型表中 gpt-image-2 重复，描述写错

**文件**: `content/docs/en/api/openai-image.mdx`  
**严重程度**: 中  

当前模型表：
```
| gpt-image-2 | GPT-Image-1 image generation and editing model... |
| gpt-image-2 | GPT-Image-2 image generation and editing model... |
```

两行 model id 相同（均为 `gpt-image-2`），第一行描述写的是 "GPT-Image-1"。  
实际测试：`gpt-image-2` 可正常调用，`gpt-image-1` 未测试（可能已下线）。

**建议修改**：
- 若 `gpt-image-1` 已下线，删除第一行
- 若 `gpt-image-1` 仍可用，第一行 model id 改为 `gpt-image-1`

---

### 问题 5：Qwen Image — qwen-image-plus 尺寸格式文档不完整

**文件**: `content/docs/en/api/qwen-image.mdx`  
**严重程度**: 中  

`qwen-image-plus` 只接受特定的尺寸值（使用 `*` 分隔符，非 `x`），实际允许的尺寸为：

```
1664*928  1472*1104  1328*1328  1104*1472  928*1664
```

调用示例中虽然写了 `"size": "1328*1328"`（正确），但正文没有说明：
1. 尺寸必须使用 `*` 作为分隔符（不是 `x`）
2. 只能从以上 5 个固定值中选择，不支持自定义尺寸

**建议修改**：在请求参数 `size` 字段说明中，明确列出允许的尺寸枚举值，并说明使用 `*` 分隔符。

---

### 问题 6：视频查询接口 — 响应中状态值与文档不一致

**文件**: `content/docs/en/api/veo-video.mdx`, `wan-video.mdx`, `seedance-2-video.mdx`  
**严重程度**: 中  

文档描述的任务状态流转为：
```
queued → in_progress → completed
                ↓
            failed
```

实际 `GET /v1/video/generations/{task_id}` 响应中的状态值：

| 端点 | Veo 实际状态值 | Wan 实际状态值 | SeeDance 实际状态值 |
|------|--------------|--------------|-------------------|
| `GET /v1/video/generations/{id}` | `"succeeded"` | `"SUCCESS"` | `"SUCCESS"` |
| `GET /v1/videos/{id}` | `"completed"` | 不适用 | 不适用 |

**建议修改**：
- 在文档中补充说明 `GET /v1/video/generations/{id}` 实际返回的状态值
- 或统一服务端状态值，保持与文档一致（建议统一为 `completed`/`failed`）

---

### 问题 7：视频查询接口 — Wan/SeeDance 响应中视频 URL 放在 fail_reason 字段

**文件**: `content/docs/en/api/wan-video.mdx`, `seedance-2-video.mdx`  
**严重程度**: 中  

`GET /v1/video/generations/{task_id}` 实际响应结构（Wan/SeeDance）：

```json
{
  "code": "success",
  "data": {
    "status": "SUCCESS",
    "fail_reason": "https://...video-url...mp4",   ← 视频 URL 放在了 fail_reason 字段
    "progress": "100%",
    "data": {
      "output": {
        "video_url": "https://...video-url...mp4"   ← 同时也在这里
      }
    }
  }
}
```

`fail_reason` 字段按语义应存放失败原因，但成功时包含了视频 URL，命名极易误导用户。  
实际视频 URL 在 `data.data.output.video_url` 路径下也可获取。

**建议修改**：在文档中补充 `GET /v1/video/generations/{id}` 的完整响应示例，并注明视频 URL 的实际取值路径（`data.data.output.video_url`），同时说明 `fail_reason` 字段在成功时的特殊含义，或建议服务端修正此字段命名。

---

### 问题 8：视频查询接口 — 响应结构有两套格式

**文件**: `content/docs/en/api/veo-video.mdx`  
**严重程度**: 低  

文档列出了两个查询接口：
- `GET /v1/video/generations/{task_id}`
- `GET /v1/videos/{task_id}`

两个接口返回结构不同：

`GET /v1/video/generations/{id}` 返回（嵌套包装）：
```json
{
  "code": "success",
  "data": { "status": "succeeded", "url": "..." }
}
```

`GET /v1/videos/{id}` 返回（扁平结构）：
```json
{
  "id": "...", "object": "video", "status": "completed", "progress": 100, "metadata": {"url": "..."}
}
```

**建议修改**：在文档中分别给出两个查询接口的完整响应示例，方便开发者按需选择。

---

### 问题 9：视频内容下载 — GET /v1/videos/{id}/content HEAD 方法返回 404

**文件**: `content/docs/en/api/veo-video.mdx`  
**严重程度**: 低  

文档列出 `GET /v1/videos/{task_id}/content` 为视频内容下载端点。  
实测：使用 GET 方法可正常返回视频二进制流；但使用 HEAD 方法返回 404。  
这是服务端配置问题，文档无需修改，可作为 bug 反馈给后端。

---

### 问题 10：管理接口 — 鉴权方式说明不够明确

**文件**: `content/docs/en/api/management/auth.mdx`  
**严重程度**: 低  

AI 模型接口使用的 `sk-...` 格式 API Key 不能用于管理接口，调用 `GET /api/user/self` 等管理接口返回：
```json
{"message": "无权进行此操作，access token 无效", "success": false}
```

文档中"系统访问令牌"和"AI API Key"的区别需要更清晰说明，建议补充一句：
> AI 模型 API Key（`sk-...` 格式）仅用于模型调用接口，不可用于管理接口；管理接口需使用在「个人设置 - 安全设置 - 系统访问令牌」中生成的 Access Token。

---

## 三、测试通过项汇总

### Chat 接口

| 接口 | 模型 | 文本 | 流式 | 函数调用 | 图片输入 |
|------|------|------|------|---------|---------|
| OpenAI `/v1/chat/completions` | gpt-3.5-turbo, gpt-4o, gpt-4o-mini, gpt-4.1, gpt-4.1-mini, gpt-4.1-nano, gpt-5, gpt-5-chat-latest, gpt-5-mini, gpt-5-nano | ✅ | ✅ | ✅ | ✅ |
| Anthropic `/v1/messages` | claude-opus-4-6, claude-opus-4-5, claude-sonnet-4-6, claude-sonnet-4-5, claude-haiku-4-5 | ✅ | ✅ | ✅ | — |
| Gemini `/v1beta/models/{model}:generateContent` | gemini-2.5-flash, gemini-2.5-pro, gemini-3-pro-preview, gemini-3-flash-preview | ✅ | ✅ | ✅ | — |
| Qwen `/api/v1/services/aigc/text-generation/generation` | qwen-turbo, qwen-plus, qwen-max | ✅ | — | — | — |

### 其他接口

| 接口 | 模型/功能 | 状态 |
|------|---------|------|
| OpenAI Embeddings `/v1/embeddings` | text-embedding-ada-002（单条+批量） | ✅ |
| OpenAI TTS `/v1/audio/speech` | tts-1, tts-1-hd | ✅ |
| OpenAI STT `/v1/audio/transcriptions` | whisper-1 | ✅ |
| OpenAI 翻译 `/v1/audio/translations` | whisper-1 | ✅ |
| OpenAI Image `/v1/images/generations` | gpt-image-2 | ✅ |
| OpenAI Image `/v1/images/edits` | gpt-image-2 | ✅ |
| Gemini Image `/v1beta/models/{model}:generateContent` | gemini-2.5-flash-image, gemini-3-pro-image-preview | ✅ |
| Qwen Image `/v1/images/generations` | qwen-image-plus（正确 size）, wan2.5-t2i-preview | ✅ |
| Qwen Image `/v1/images/edits` | qwen-image-edit-plus, qwen-image-edit | ✅ |
| Veo Video 提交 `/v1/video/generations` | veo-3.0-generate-001, veo-3.0-fast-generate-001 | ✅ |
| Veo Video 查询 `/v1/videos/{id}` | 返回 `status: completed`, 含视频 URL | ✅ |
| Wan Video 提交/查询 | wan2.5-t2v-preview, wan2.6-t2v | ✅ |
| SeeDance 提交/查询 | doubao-seedance-2-0-fast-260128, doubao-seedance-2-0-260128, dreamina-seedance-2-0-fast-260128, dreamina-seedance-2-0-260128 | ✅ |
| 系统状态 `GET /api/status` | — | ✅ |
| 模型列表 `GET /v1/models` | — | ✅ |

---

## 四、待进一步确认的问题

1. **gpt-image-1 是否存在？** 文档第一行 model 名写 `gpt-image-2` 但描述写 `GPT-Image-1`，需确认是笔误还是有 `gpt-image-1` 这个 model id。

2. **wan2.5-i2i-preview 成功时是否也返回 HTTP 200 + 错误体？** 测试时使用了最小图片（1×1 px）触发了尺寸校验错误，图片符合要求时是否正常返回尚未验证。建议用合规图片（≥384px）重测。

3. **Veo image-to-video 和 Wan image-to-video 接口** 因需要提供真实图片未完整测试，建议手动验证。

4. **管理接口全量测试** 需要提供管理员 Access Token（非 AI API Key）才能完整覆盖。
