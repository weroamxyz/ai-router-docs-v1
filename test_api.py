#!/usr/bin/env python3
"""
AI Router API 综合测试脚本
验证接口文档中所有罗列的 API 接口形式和模型是否准确可用。

使用方法:
    export API_KEY="your-api-key"
    export API_BASE_URL="https://computevault.unodetech.xyz"   # 可选，有默认值
    export MANAGEMENT_TOKEN="your-management-token"            # 可选，用于管理接口
    export TEST_VIDEO="1"                                      # 可选，开启视频生成测试（耗时长）
    export TEST_ALL_MODELS="1"                                 # 可选，测试所有模型（默认只测代表性模型）

    python test_api.py                          # 运行所有测试
    python test_api.py --category chat          # 只测 chat 接口
    python test_api.py --category embed         # 只测 embeddings
    python test_api.py --category audio         # 只测 audio
    python test_api.py --category image         # 只测 image
    python test_api.py --category video         # 只测 video
    python test_api.py --category management    # 只测管理接口
    python test_api.py --list                   # 列出所有测试项
"""

import os
import sys
import json
import time
import base64
import struct
import io
import argparse
import traceback
import requests
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple

# ============================================================
# 配置
# ============================================================
BASE_URL = os.environ.get("API_BASE_URL", "https://computevault.unodetech.xyz").rstrip("/")
API_KEY = os.environ.get("API_KEY", "")
MANAGEMENT_TOKEN = os.environ.get("MANAGEMENT_TOKEN", API_KEY)
TEST_VIDEO = os.environ.get("TEST_VIDEO", "0") == "1"
TEST_ALL_MODELS = os.environ.get("TEST_ALL_MODELS", "0") == "1"

REQUEST_TIMEOUT = 60          # 普通请求超时（秒）
VIDEO_POLL_TIMEOUT = 600      # 视频任务最长等待（秒）
VIDEO_POLL_INTERVAL = 15      # 视频轮询间隔（秒）

# ============================================================
# 颜色输出
# ============================================================
def green(s):  return f"\033[92m{s}\033[0m"
def red(s):    return f"\033[91m{s}\033[0m"
def yellow(s): return f"\033[93m{s}\033[0m"
def cyan(s):   return f"\033[96m{s}\033[0m"
def bold(s):   return f"\033[1m{s}\033[0m"

# ============================================================
# 结果收集
# ============================================================
class TestResult:
    def __init__(self, category, name, model, passed, status_code=None, note="", doc_issue=False):
        self.category   = category
        self.name       = name
        self.model      = model
        self.passed     = passed
        self.status_code = status_code
        self.note       = note
        self.doc_issue  = doc_issue  # 文档本身有问题

all_results: List[TestResult] = []
doc_issues: List[str] = []

def record(category, name, model, passed, status_code=None, note="", doc_issue=False):
    r = TestResult(category, name, model, passed, status_code, note, doc_issue)
    all_results.append(r)
    icon = green("✓") if passed else red("✗")
    tag = f" {yellow('[DOC ISSUE]')}" if doc_issue else ""
    print(f"  {icon} [{category}] {name} | model={model or '-'} | HTTP {status_code or '?'}{tag}")
    if note:
        print(f"      → {note}")
    return r

# ============================================================
# HTTP 助手
# ============================================================
def openai_headers():
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

def anthropic_headers():
    return {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }

def management_headers(user_id=None):
    h = {
        "Authorization": f"Bearer {MANAGEMENT_TOKEN}",
        "Content-Type": "application/json",
    }
    if user_id:
        h["New-Api-User"] = str(user_id)
    return h

def post(url, headers, body, timeout=REQUEST_TIMEOUT, stream=False):
    try:
        resp = requests.post(url, headers=headers, json=body, timeout=timeout, stream=stream)
        return resp
    except requests.exceptions.Timeout:
        return None
    except Exception as e:
        return None

def get(url, headers=None, params=None, timeout=REQUEST_TIMEOUT):
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=timeout)
        return resp
    except Exception:
        return None

def validate_response(resp, expected_keys=None, expected_status=200):
    """返回 (passed, note)"""
    if resp is None:
        return False, "请求超时或连接失败"
    if resp.status_code != expected_status:
        try:
            body = resp.json()
            msg = body.get("error", {}).get("message", "") or str(body)[:120]
        except Exception:
            msg = resp.text[:120]
        return False, f"HTTP {resp.status_code}: {msg}"
    if expected_keys:
        try:
            body = resp.json()
        except Exception:
            return False, "响应不是合法 JSON"
        missing = [k for k in expected_keys if k not in body]
        if missing:
            return False, f"响应缺少字段: {missing}"
    return True, ""

def make_tiny_wav():
    """生成一个最小有效 WAV 文件（静音），用于 STT 测试"""
    # 44字节 WAV 头 + 2字节静音样本
    sample_rate = 8000
    num_channels = 1
    bits = 16
    num_samples = 800  # 0.1 秒
    data_size = num_samples * num_channels * (bits // 8)
    chunk_size = 36 + data_size
    buf = io.BytesIO()
    buf.write(b"RIFF")
    buf.write(struct.pack("<I", chunk_size))
    buf.write(b"WAVE")
    buf.write(b"fmt ")
    buf.write(struct.pack("<IHHIIHH", 16, 1, num_channels, sample_rate,
                          sample_rate * num_channels * bits // 8,
                          num_channels * bits // 8, bits))
    buf.write(b"data")
    buf.write(struct.pack("<I", data_size))
    buf.write(b"\x00" * data_size)
    buf.seek(0)
    return buf.read()

def make_tiny_png():
    """生成一个最小有效 1×1 白色 PNG 图片"""
    import zlib
    def _chunk(name, data):
        crc = zlib.crc32(name + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + name + data + struct.pack(">I", crc)
    signature = b"\x89PNG\r\n\x1a\n"
    ihdr = _chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
    raw = b"\x00\xFF\xFF\xFF"  # filter byte + RGB
    idat = _chunk(b"IDAT", zlib.compress(raw))
    iend = _chunk(b"IEND", b"")
    return signature + ihdr + idat + iend

# ============================================================
# 注意: 记录的文档问题
# ============================================================
def note_doc_issue(msg):
    doc_issues.append(msg)
    print(f"  {yellow('[DOC ISSUE]')} {msg}")

# ============================================================
# 1. OpenAI Chat Completions (POST /v1/chat/completions)
# ============================================================
OPENAI_CHAT_MODELS = [
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-16k",
    "gpt-3.5-turbo-instruct",
    "gpt-4",
    "gpt-4-32k",
    "gpt-4-turbo-preview",
    "gpt-4-turbo",
    "gpt-4-vision-preview",
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4.5-preview",
    "gpt-4.1",
    "gpt-4.1-mini",
    "gpt-4.1-nano",
    "gpt-5",
    "gpt-5-chat-latest",
    "gpt-5-mini",
    "gpt-5-nano",
]

# 代表性模型（TEST_ALL_MODELS=0 时使用）
OPENAI_CHAT_KEY_MODELS = ["gpt-4o-mini", "gpt-4.1-mini"]

def test_openai_chat(model, stream=False):
    url = f"{BASE_URL}/v1/chat/completions"
    body = {
        "model": model,
        "messages": [{"role": "user", "content": "Reply with exactly: ok"}],
        "max_tokens": 5,
        "stream": stream,
    }
    resp = post(url, openai_headers(), body)
    if stream:
        if resp is None:
            return record("openai-chat", "streaming", model, False, note="连接失败")
        passed = resp.status_code == 200
        note = "" if passed else f"HTTP {resp.status_code}"
        return record("openai-chat", "streaming", model, passed, resp.status_code, note)

    passed, note = validate_response(resp, ["id", "choices", "usage"])
    return record("openai-chat", "text-chat", model, passed,
                  resp.status_code if resp else None, note)

def test_openai_chat_function_calling(model="gpt-4o-mini"):
    url = f"{BASE_URL}/v1/chat/completions"
    body = {
        "model": model,
        "messages": [{"role": "user", "content": "What is the weather in Beijing?"}],
        "tools": [{
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get current weather",
                "parameters": {
                    "type": "object",
                    "properties": {"location": {"type": "string"}},
                    "required": ["location"],
                },
            },
        }],
        "tool_choice": "auto",
        "max_tokens": 50,
    }
    resp = post(url, openai_headers(), body)
    passed, note = validate_response(resp, ["id", "choices"])
    return record("openai-chat", "function-calling", model, passed,
                  resp.status_code if resp else None, note)

def test_openai_chat_image(model="gpt-4o-mini"):
    url = f"{BASE_URL}/v1/chat/completions"
    body = {
        "model": model,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": "What color is this?"},
                {"type": "image_url", "image_url": {
                    "url": "data:image/png;base64," + base64.b64encode(make_tiny_png()).decode()
                }},
            ],
        }],
        "max_tokens": 10,
    }
    resp = post(url, openai_headers(), body)
    passed, note = validate_response(resp, ["id", "choices"])
    return record("openai-chat", "image-input", model, passed,
                  resp.status_code if resp else None, note)

def run_openai_chat_tests():
    print(bold(f"\n{'='*60}"))
    print(bold("OpenAI Chat Completions  POST /v1/chat/completions"))
    print(bold(f"{'='*60}"))
    models = OPENAI_CHAT_MODELS if TEST_ALL_MODELS else OPENAI_CHAT_KEY_MODELS
    for m in models:
        test_openai_chat(m)
    # 功能测试（只用代表性模型）
    test_openai_chat(OPENAI_CHAT_KEY_MODELS[0], stream=True)
    test_openai_chat_function_calling()
    test_openai_chat_image()

# ============================================================
# 2. Anthropic Messages (POST /v1/messages)
# ============================================================
ANTHROPIC_MODELS = [
    "claude-opus-4-6",
    "claude-opus-4-5",
    "claude-sonnet-4-6",
    "claude-sonnet-4-5",
    "claude-haiku-4-5",
]
ANTHROPIC_KEY_MODELS = ["claude-haiku-4-5", "claude-sonnet-4-6"]

def test_anthropic_chat(model, stream=False):
    url = f"{BASE_URL}/v1/messages"
    body = {
        "model": model,
        "max_tokens": 10,
        "messages": [{"role": "user", "content": "Reply with exactly: ok"}],
        "stream": stream,
    }
    resp = post(url, anthropic_headers(), body)
    if stream:
        if resp is None:
            return record("anthropic", "streaming", model, False, note="连接失败")
        passed = resp.status_code == 200
        note = "" if passed else f"HTTP {resp.status_code}"
        return record("anthropic", "streaming", model, passed, resp.status_code, note)

    passed, note = validate_response(resp, ["id", "content", "usage"])
    return record("anthropic", "text-chat", model, passed,
                  resp.status_code if resp else None, note)

def test_anthropic_tool_calling(model="claude-haiku-4-5"):
    url = f"{BASE_URL}/v1/messages"
    body = {
        "model": model,
        "max_tokens": 100,
        "messages": [{"role": "user", "content": "What is the weather in Beijing?"}],
        "tools": [{
            "name": "get_weather",
            "description": "Get current weather for a location",
            "input_schema": {
                "type": "object",
                "properties": {"location": {"type": "string", "description": "City name"}},
                "required": ["location"],
            },
        }],
    }
    resp = post(url, anthropic_headers(), body)
    passed, note = validate_response(resp, ["id", "content"])
    return record("anthropic", "tool-calling", model, passed,
                  resp.status_code if resp else None, note)

def run_anthropic_tests():
    print(bold(f"\n{'='*60}"))
    print(bold("Anthropic Messages  POST /v1/messages"))
    print(bold(f"{'='*60}"))
    models = ANTHROPIC_MODELS if TEST_ALL_MODELS else ANTHROPIC_KEY_MODELS
    for m in models:
        test_anthropic_chat(m)
    test_anthropic_chat(ANTHROPIC_KEY_MODELS[0], stream=True)
    test_anthropic_tool_calling()

# ============================================================
# 3. Google Gemini Chat (POST /v1beta/models/{model}:generateContent)
# ============================================================
GEMINI_CHAT_MODELS = [
    "gemini-1.5-pro",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
    "gemini-1.5-pro-latest",
    "gemini-1.5-flash-latest",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite-preview",
    "gemini-2.0-flash-exp",
    "gemini-2.0-pro-exp",
    "gemini-2.0-flash-thinking-exp",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-3-pro-preview",
    "gemini-3-flash-preview",
]
GEMINI_KEY_MODELS = ["gemini-2.0-flash", "gemini-2.5-flash"]

def test_gemini_chat(model, stream=False):
    endpoint = "streamGenerateContent" if stream else "generateContent"
    url = f"{BASE_URL}/v1beta/models/{model}:{endpoint}"
    params = {"key": API_KEY}
    if stream:
        params["alt"] = "sse"
    body = {
        "contents": [{"parts": [{"text": "Reply with exactly: ok"}]}],
        "generationConfig": {"maxOutputTokens": 10},
    }
    try:
        resp = requests.post(url, params=params, json=body, timeout=REQUEST_TIMEOUT)
    except Exception:
        resp = None

    name = "streaming" if stream else "text-chat"
    if resp is None:
        return record("gemini-chat", name, model, False, note="连接失败")
    if stream:
        passed = resp.status_code == 200
        return record("gemini-chat", name, model, passed, resp.status_code,
                      "" if passed else f"HTTP {resp.status_code}")

    passed, note = validate_response(resp, ["candidates"])
    return record("gemini-chat", name, model, passed, resp.status_code if resp else None, note)

def test_gemini_function_calling(model="gemini-2.0-flash"):
    url = f"{BASE_URL}/v1beta/models/{model}:generateContent"
    params = {"key": API_KEY}
    body = {
        "contents": [{"parts": [{"text": "Turn on the lights."}]}],
        "tools": [{"function_declarations": [{"name": "enable_lights", "description": "Turn on the lighting system."}]}],
        "generationConfig": {"maxOutputTokens": 50},
    }
    try:
        resp = requests.post(url, params=params, json=body, timeout=REQUEST_TIMEOUT)
    except Exception:
        resp = None
    passed, note = validate_response(resp, ["candidates"])
    return record("gemini-chat", "function-calling", model, passed,
                  resp.status_code if resp else None, note)

def run_gemini_chat_tests():
    print(bold(f"\n{'='*60}"))
    print(bold("Google Gemini Chat  POST /v1beta/models/{model}:generateContent"))
    print(bold(f"{'='*60}"))
    models = GEMINI_CHAT_MODELS if TEST_ALL_MODELS else GEMINI_KEY_MODELS
    for m in models:
        test_gemini_chat(m)
    test_gemini_chat(GEMINI_KEY_MODELS[0], stream=True)
    test_gemini_function_calling()

# ============================================================
# 4. Qwen Chat (POST /api/v1/services/aigc/text-generation/generation)
# ============================================================
QWEN_CHAT_MODELS = ["qwen-turbo", "qwen-plus", "qwen-max"]
QWEN_KEY_MODELS = ["qwen-turbo"]

def test_qwen_chat(model):
    url = f"{BASE_URL}/api/v1/services/aigc/text-generation/generation"
    body = {
        "model": model,
        "input": {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Reply with exactly: ok"},
            ]
        },
    }
    resp = post(url, openai_headers(), body)
    # Qwen 响应格式: {"output": {"choices": [...]}, "usage": {...}, "request_id": "..."}
    if resp is None:
        return record("qwen-chat", "text-chat", model, False, note="连接失败")
    if resp.status_code != 200:
        try:
            msg = resp.json().get("message", resp.text[:120])
        except Exception:
            msg = resp.text[:120]
        return record("qwen-chat", "text-chat", model, False, resp.status_code, msg)
    try:
        body_resp = resp.json()
        passed = "output" in body_resp
        note = "" if passed else f"缺少 output 字段, 实际: {list(body_resp.keys())}"
    except Exception:
        passed, note = False, "响应非 JSON"
    return record("qwen-chat", "text-chat", model, passed, resp.status_code, note)

def run_qwen_chat_tests():
    print(bold(f"\n{'='*60}"))
    print(bold("Qwen Chat  POST /api/v1/services/aigc/text-generation/generation"))
    print(bold(f"{'='*60}"))
    models = QWEN_CHAT_MODELS if TEST_ALL_MODELS else QWEN_KEY_MODELS
    for m in models:
        test_qwen_chat(m)

# ============================================================
# 5. OpenAI Embeddings (POST /v1/embeddings)
# ============================================================
EMBEDDING_MODELS = ["text-embedding-ada-002"]

def test_embedding(model, batch=False):
    url = f"{BASE_URL}/v1/embeddings"
    inp = ["hello world", "goodbye"] if batch else "hello world"
    body = {"input": inp, "model": model, "encoding_format": "float"}
    resp = post(url, openai_headers(), body)
    passed, note = validate_response(resp, ["object", "data", "model", "usage"])
    if passed:
        try:
            data = resp.json()["data"]
            if not isinstance(data, list) or len(data) == 0:
                passed, note = False, "data 字段为空列表"
            elif "embedding" not in data[0]:
                passed, note = False, "embedding 字段缺失"
        except Exception:
            pass
    name = "batch-embed" if batch else "single-embed"
    return record("embeddings", name, model, passed,
                  resp.status_code if resp else None, note)

def run_embedding_tests():
    print(bold(f"\n{'='*60}"))
    print(bold("OpenAI Embeddings  POST /v1/embeddings"))
    print(bold(f"{'='*60}"))
    for m in EMBEDDING_MODELS:
        test_embedding(m)
        test_embedding(m, batch=True)

# ============================================================
# 6. OpenAI Audio
# ============================================================
TTS_MODELS = ["tts-1", "tts-1-hd"]

def test_tts(model, voice="alloy"):
    url = f"{BASE_URL}/v1/audio/speech"
    body = {"model": model, "input": "Hello.", "voice": voice}
    resp = post(url, openai_headers(), body)
    if resp is None:
        return record("audio-tts", "text-to-speech", model, False, note="连接失败"), None
    passed = resp.status_code == 200 and len(resp.content) > 0
    note = "" if passed else f"HTTP {resp.status_code}, size={len(resp.content) if resp else 0}"
    r = record("audio-tts", "text-to-speech", model, passed, resp.status_code, note)
    audio_bytes = resp.content if passed else None
    return r, audio_bytes

def test_stt(audio_bytes, model="whisper-1"):
    """语音转文字（需要音频字节）"""
    url = f"{BASE_URL}/v1/audio/transcriptions"
    if audio_bytes is None:
        audio_bytes = make_tiny_wav()
    try:
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {API_KEY}"},
            files={"file": ("audio.mp3", audio_bytes, "audio/mpeg")},
            data={"model": model},
            timeout=REQUEST_TIMEOUT,
        )
    except Exception:
        resp = None
    if resp is None:
        return record("audio-stt", "speech-to-text", model, False, note="连接失败")
    passed = resp.status_code == 200
    try:
        body = resp.json()
        passed = passed and "text" in body
        note = "" if passed else f"缺少 text 字段"
    except Exception:
        note = f"HTTP {resp.status_code}"
        passed = False
    return record("audio-stt", "speech-to-text", model, passed, resp.status_code, note)

def test_translation(audio_bytes, model="whisper-1"):
    url = f"{BASE_URL}/v1/audio/translations"
    if audio_bytes is None:
        audio_bytes = make_tiny_wav()
    try:
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {API_KEY}"},
            files={"file": ("audio.mp3", audio_bytes, "audio/mpeg")},
            data={"model": model},
            timeout=REQUEST_TIMEOUT,
        )
    except Exception:
        resp = None
    if resp is None:
        return record("audio-translate", "audio-translation", model, False, note="连接失败")
    passed = resp.status_code == 200
    try:
        body = resp.json()
        passed = passed and "text" in body
    except Exception:
        passed = False
    note = "" if passed else f"HTTP {resp.status_code}"
    return record("audio-translate", "audio-translation", model, passed, resp.status_code, note)

def run_audio_tests():
    print(bold(f"\n{'='*60}"))
    print(bold("OpenAI Audio  /v1/audio/*"))
    print(bold(f"{'='*60}"))
    models = TTS_MODELS if TEST_ALL_MODELS else ["tts-1"]
    saved_audio = None
    for m in models:
        _, audio_bytes = test_tts(m)
        if audio_bytes and saved_audio is None:
            saved_audio = audio_bytes

    # STT 和翻译使用 TTS 生成的音频（或静音 WAV fallback）
    test_stt(saved_audio)
    test_translation(saved_audio)

# ============================================================
# 7. OpenAI Image (POST /v1/images/generations  &  /v1/images/edits)
# ============================================================
# 文档问题: openai-image.mdx 表格中 gpt-image-2 出现两次，
# 第一行描述写的是 "GPT-Image-1" 但 model id 也是 "gpt-image-2"，疑似笔误
OPENAI_IMAGE_MODELS_DOC = ["gpt-image-2", "gpt-image-2"]  # 文档中重复了

def test_openai_image_gen(model="gpt-image-2"):
    url = f"{BASE_URL}/v1/images/generations"
    body = {
        "model": model,
        "prompt": "a red circle",
        "n": 1,
        "size": "1024x1024",
        "quality": "low",
    }
    resp = post(url, openai_headers(), body, timeout=120)
    if resp is None:
        return record("openai-image", "image-gen", model, False, note="连接失败/超时")
    passed = resp.status_code == 200
    if passed:
        try:
            body_resp = resp.json()
            passed = "data" in body_resp and len(body_resp["data"]) > 0
            note = "" if passed else "data 字段为空"
        except Exception:
            passed, note = False, "响应非 JSON"
    else:
        try:
            msg = resp.json().get("error", {}).get("message", resp.text[:120])
        except Exception:
            msg = resp.text[:120]
        note = msg
    return record("openai-image", "image-gen", model, passed, resp.status_code, note)

def test_openai_image_edit(model="gpt-image-2"):
    url = f"{BASE_URL}/v1/images/edits"
    png_bytes = make_tiny_png()
    try:
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {API_KEY}"},
            files={
                "image": ("image.png", png_bytes, "image/png"),
            },
            data={
                "model": model,
                "prompt": "make it blue",
                "size": "1024x1024",
            },
            timeout=120,
        )
    except Exception:
        resp = None
    if resp is None:
        return record("openai-image", "image-edit", model, False, note="连接失败/超时")
    passed = resp.status_code == 200
    try:
        body_resp = resp.json()
        passed = passed and "data" in body_resp
    except Exception:
        passed = False
    note = "" if passed else f"HTTP {resp.status_code}"
    return record("openai-image", "image-edit", model, passed, resp.status_code, note)

def run_openai_image_tests():
    print(bold(f"\n{'='*60}"))
    print(bold("OpenAI Image  /v1/images/*"))
    print(bold(f"{'='*60}"))
    # 文档问题提示
    if len(set(OPENAI_IMAGE_MODELS_DOC)) < len(OPENAI_IMAGE_MODELS_DOC):
        note_doc_issue(
            "openai-image.mdx: 支持的模型表中 'gpt-image-2' 重复出现两次，"
            "第一行描述为 'GPT-Image-1' 但 model id 也写成 'gpt-image-2'，"
            "疑似应为 'gpt-image-1'。"
        )
    test_openai_image_gen()
    test_openai_image_edit()

# ============================================================
# 8. Gemini Image (POST /v1beta/models/{model}:generateContent)
# ============================================================
GEMINI_IMAGE_MODELS = ["gemini-2.5-flash-image", "gemini-3-pro-image-preview"]
GEMINI_IMAGE_KEY_MODELS = ["gemini-2.5-flash-image"]

def test_gemini_image_gen(model):
    url = f"{BASE_URL}/v1beta/models/{model}:generateContent"
    params = {"key": API_KEY}
    body = {
        "contents": [{"parts": [{"text": "Give me an image of a red circle."}]}],
        "generationConfig": {"responseModalities": ["IMAGE", "TEXT"]},
    }
    try:
        resp = requests.post(url, params=params, json=body, timeout=120)
    except Exception:
        resp = None
    if resp is None:
        return record("gemini-image", "image-gen", model, False, note="连接失败/超时")
    passed = resp.status_code == 200
    if passed:
        try:
            body_resp = resp.json()
            passed = "candidates" in body_resp
            note = "" if passed else "缺少 candidates 字段"
        except Exception:
            passed, note = False, "响应非 JSON"
    else:
        try:
            msg = resp.json().get("error", {}).get("message", resp.text[:120])
        except Exception:
            msg = resp.text[:120]
        note = msg
    return record("gemini-image", "image-gen", model, passed, resp.status_code, note)

def run_gemini_image_tests():
    print(bold(f"\n{'='*60}"))
    print(bold("Gemini Image  POST /v1beta/models/{model}:generateContent"))
    print(bold(f"{'='*60}"))
    models = GEMINI_IMAGE_MODELS if TEST_ALL_MODELS else GEMINI_IMAGE_KEY_MODELS
    for m in models:
        test_gemini_image_gen(m)

# ============================================================
# 9. Qwen Image (POST /v1/images/generations  &  /v1/images/edits)
# ============================================================
QWEN_IMAGE_GEN_MODELS = ["qwen-image-plus", "wan2.5-t2i-preview"]
QWEN_IMAGE_EDIT_MODELS = ["qwen-image-edit-plus", "qwen-image-edit", "wan2.5-i2i-preview"]
QWEN_IMAGE_KEY_GEN = ["qwen-image-plus"]

def test_qwen_image_gen(model):
    url = f"{BASE_URL}/v1/images/generations"
    body = {
        "model": model,
        "prompt": "a red circle",
        "n": 1,
        "size": "1024x1024",
    }
    resp = post(url, openai_headers(), body, timeout=120)
    if resp is None:
        return record("qwen-image", "image-gen", model, False, note="连接失败/超时")
    passed = resp.status_code == 200
    if passed:
        try:
            data = resp.json()
            passed = "data" in data and len(data["data"]) > 0
            note = "" if passed else "data 字段为空"
        except Exception:
            passed, note = False, "响应非 JSON"
    else:
        try:
            msg = resp.json().get("error", {}).get("message", resp.text[:120])
        except Exception:
            msg = resp.text[:120]
        note = msg
    return record("qwen-image", "image-gen", model, passed, resp.status_code, note)

def test_qwen_image_edit(model):
    url = f"{BASE_URL}/v1/images/edits"
    png_bytes = make_tiny_png()
    try:
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {API_KEY}"},
            files={"image": ("image.png", png_bytes, "image/png")},
            data={"model": model, "prompt": "make it blue"},
            timeout=120,
        )
    except Exception:
        resp = None
    if resp is None:
        return record("qwen-image", "image-edit", model, False, note="连接失败/超时")
    passed = resp.status_code == 200
    try:
        body = resp.json()
        passed = passed and "data" in body
    except Exception:
        passed = False
    note = "" if passed else f"HTTP {resp.status_code}"
    return record("qwen-image", "image-edit", model, passed, resp.status_code, note)

def run_qwen_image_tests():
    print(bold(f"\n{'='*60}"))
    print(bold("Qwen Image  POST /v1/images/*"))
    print(bold(f"{'='*60}"))
    models_gen = QWEN_IMAGE_GEN_MODELS if TEST_ALL_MODELS else QWEN_IMAGE_KEY_GEN
    for m in models_gen:
        test_qwen_image_gen(m)
    if TEST_ALL_MODELS:
        for m in QWEN_IMAGE_EDIT_MODELS:
            test_qwen_image_edit(m)

# ============================================================
# 10. Video Generation (async, POST /v1/video/generations)
# ============================================================
def submit_video_task(model, prompt, metadata=None):
    url = f"{BASE_URL}/v1/video/generations"
    body = {"model": model, "prompt": prompt}
    if metadata:
        body["metadata"] = metadata
    resp = post(url, openai_headers(), body, timeout=60)
    return resp

def poll_video_task(task_id):
    url = f"{BASE_URL}/v1/video/generations/{task_id}"
    deadline = time.time() + VIDEO_POLL_TIMEOUT
    while time.time() < deadline:
        resp = get(url, openai_headers())
        if resp is None:
            return "error", None
        try:
            body = resp.json()
            status = body.get("status", "unknown")
            if status in ("completed", "failed"):
                return status, body
        except Exception:
            return "error", None
        time.sleep(VIDEO_POLL_INTERVAL)
    return "timeout", None

def test_video(model, category, prompt="A cat walking in a garden.", metadata=None):
    resp = submit_video_task(model, prompt, metadata)
    if resp is None:
        return record(category, "video-gen-submit", model, False, note="提交失败/超时")

    if resp.status_code not in (200, 201, 202):
        try:
            msg = resp.json().get("error", {}).get("message", resp.text[:120])
        except Exception:
            msg = resp.text[:120]
        return record(category, "video-gen-submit", model, False, resp.status_code, msg)

    # 任务提交成功
    try:
        body = resp.json()
        task_id = body.get("id") or body.get("task_id")
    except Exception:
        task_id = None

    record(category, "video-gen-submit", model, True, resp.status_code,
           f"task_id={task_id}")

    if task_id is None:
        return record(category, "video-gen-poll", model, False, note="响应中无 task_id")

    print(f"      → 轮询任务 {task_id}（最长等待 {VIDEO_POLL_TIMEOUT}s）...")
    final_status, result_body = poll_video_task(task_id)
    passed = final_status == "completed"
    note = f"最终状态: {final_status}"
    if result_body and final_status == "failed":
        note += f" | {result_body.get('error', '')}"
    return record(category, "video-gen-poll", model, passed, note=note)

VEO_MODELS_DOC = [
    "veo-3.0-generate-001",
    "veo-3.0-fast-generate-001",
    "veo-3.1-generate-001",
    "veo-3.1-fast-generate-001",
]
WAN_MODELS_DOC = ["wan2.5-t2v-preview", "wan2.6-t2v"]
SEEDANCE_MODELS_DOC = [
    "doubao-seedance-2-0-fast-260128",
    "doubao-seedance-2-0-260128",
    "dreamina-seedance-2-0-fast-260128",
    "dreamina-seedance-2-0-260128",
]

def run_video_tests():
    print(bold(f"\n{'='*60}"))
    print(bold("Video Generation  POST /v1/video/generations"))
    print(bold(f"{'='*60}"))
    if not TEST_VIDEO:
        print(yellow("  [跳过] 视频测试已禁用，设置环境变量 TEST_VIDEO=1 启用"))
        return

    # Veo 测试（只测最快的）
    veo_models = VEO_MODELS_DOC if TEST_ALL_MODELS else ["veo-3.0-fast-generate-001"]
    for m in veo_models:
        test_video(m, "veo-video", metadata={"durationSeconds": 5, "aspectRatio": "16:9"})

    # Wan 测试
    wan_models = WAN_MODELS_DOC if TEST_ALL_MODELS else ["wan2.6-t2v"]
    for m in wan_models:
        test_video(m, "wan-video", metadata={
            "parameters": {"size": "1280*720"},
        })

    # SeeDance 测试
    seedance_models = SEEDANCE_MODELS_DOC if TEST_ALL_MODELS else ["doubao-seedance-2-0-fast-260128"]
    for m in seedance_models:
        test_video(m, "seedance-video")

# ============================================================
# 11. Management APIs
# ============================================================
def test_management_public():
    """无需鉴权的公开接口"""
    # GET /api/status
    resp = get(f"{BASE_URL}/api/status")
    if resp is None:
        return record("management", "GET /api/status", None, False, note="连接失败")
    passed = resp.status_code == 200
    try:
        body = resp.json()
        note = f"success={body.get('success', '?')}"
    except Exception:
        note = f"HTTP {resp.status_code}"
    record("management-public", "GET /api/status", None, passed, resp.status_code, note)

def test_management_models_list():
    """GET /v1/models - 列出模型（OpenAI 格式）"""
    resp = get(f"{BASE_URL}/v1/models", openai_headers())
    passed, note = validate_response(resp, ["object", "data"])
    record("management-public", "GET /v1/models", None, passed,
           resp.status_code if resp else None, note)

def test_management_user_self():
    """GET /api/user/self - 需要用户 token"""
    if not MANAGEMENT_TOKEN:
        record("management-user", "GET /api/user/self", None, False, note="未设置 MANAGEMENT_TOKEN")
        return
    resp = get(f"{BASE_URL}/api/user/self", management_headers())
    if resp is None:
        return record("management-user", "GET /api/user/self", None, False, note="连接失败")
    passed = resp.status_code == 200
    try:
        body = resp.json()
        passed = passed and body.get("success", False)
        note = f"success={body.get('success')}"
    except Exception:
        note = f"HTTP {resp.status_code}"
        passed = False
    record("management-user", "GET /api/user/self", None, passed, resp.status_code, note)

def test_management_token_list():
    """GET /api/token - 令牌列表（需要用户 token）"""
    if not MANAGEMENT_TOKEN:
        record("management-user", "GET /api/token", None, False, note="未设置 MANAGEMENT_TOKEN")
        return
    resp = get(f"{BASE_URL}/api/token", management_headers(), params={"p": 1, "page_size": 5})
    if resp is None:
        return record("management-user", "GET /api/token", None, False, note="连接失败")
    passed = resp.status_code == 200
    try:
        body = resp.json()
        note = f"success={body.get('success')}"
    except Exception:
        note = f"HTTP {resp.status_code}"
        passed = False
    record("management-user", "GET /api/token", None, passed, resp.status_code, note)

def test_management_log_self():
    """GET /api/log/self - 自己的日志（需要用户 token）"""
    if not MANAGEMENT_TOKEN:
        return
    resp = get(f"{BASE_URL}/api/log/self", management_headers(), params={"p": 1, "page_size": 5})
    if resp is None:
        return record("management-user", "GET /api/log/self", None, False, note="连接失败")
    passed = resp.status_code == 200
    try:
        body = resp.json()
        note = f"success={body.get('success')}"
    except Exception:
        note = f"HTTP {resp.status_code}"
        passed = False
    record("management-user", "GET /api/log/self", None, passed, resp.status_code, note)

def test_management_admin_channels():
    """GET /api/channel - 渠道管理（需要 admin token）"""
    if not MANAGEMENT_TOKEN:
        return
    resp = get(f"{BASE_URL}/api/channel", management_headers(), params={"p": 1, "page_size": 5})
    if resp is None:
        return record("management-admin", "GET /api/channel", None, False, note="连接失败")
    passed = resp.status_code == 200
    try:
        body = resp.json()
        note = f"success={body.get('success')}"
    except Exception:
        note = f"HTTP {resp.status_code}"
        passed = False
    record("management-admin", "GET /api/channel", None, passed, resp.status_code, note)

def test_management_admin_users():
    """GET /api/user - 用户管理（需要 admin token）"""
    if not MANAGEMENT_TOKEN:
        return
    resp = get(f"{BASE_URL}/api/user", management_headers(), params={"p": 1, "page_size": 5})
    if resp is None:
        return record("management-admin", "GET /api/user", None, False, note="连接失败")
    passed = resp.status_code == 200
    try:
        body = resp.json()
        note = f"success={body.get('success')}"
    except Exception:
        note = f"HTTP {resp.status_code}"
        passed = False
    record("management-admin", "GET /api/user", None, passed, resp.status_code, note)

def run_management_tests():
    print(bold(f"\n{'='*60}"))
    print(bold("Management APIs  /api/*"))
    print(bold(f"{'='*60}"))
    test_management_public()
    test_management_models_list()
    test_management_user_self()
    test_management_token_list()
    test_management_log_self()
    test_management_admin_channels()
    test_management_admin_users()

# ============================================================
# 汇总报告
# ============================================================
def print_summary():
    total = len(all_results)
    passed = sum(1 for r in all_results if r.passed)
    failed = total - passed

    print(bold(f"\n{'='*60}"))
    print(bold("测试汇总"))
    print(bold(f"{'='*60}"))
    print(f"  总测试数: {total}")
    print(f"  {green('通过')}: {passed}")
    print(f"  {red('失败')}: {failed}")
    print(f"  通过率: {passed/total*100:.1f}%" if total > 0 else "  无测试")

    if failed > 0:
        print(bold(f"\n失败项列表:"))
        for r in all_results:
            if not r.passed:
                print(f"  {red('✗')} [{r.category}] {r.name} | model={r.model or '-'} | {r.note}")

    if doc_issues:
        print(bold(f"\n{yellow('文档问题')}（共 {len(doc_issues)} 个）:"))
        for i, issue in enumerate(doc_issues, 1):
            print(f"  {i}. {issue}")

    # 按 category 统计
    from collections import defaultdict
    cat_stats = defaultdict(lambda: [0, 0])
    for r in all_results:
        cat_stats[r.category][0 if r.passed else 1] += 1
    print(bold(f"\n各类别统计:"))
    for cat, (p, f) in sorted(cat_stats.items()):
        bar = green("✓") * p + red("✗") * f
        print(f"  {cat:<30} 通过={p} 失败={f}  {bar}")

# ============================================================
# --list 功能
# ============================================================
def print_list():
    print(bold("所有测试项列表:\n"))

    print(bold("── Chat ──"))
    print(f"  OpenAI Chat ({len(OPENAI_CHAT_MODELS)} models): POST /v1/chat/completions")
    for m in OPENAI_CHAT_MODELS:
        print(f"    - {m}")
    print(f"  Anthropic ({len(ANTHROPIC_MODELS)} models): POST /v1/messages")
    for m in ANTHROPIC_MODELS:
        print(f"    - {m}")
    print(f"  Gemini Chat ({len(GEMINI_CHAT_MODELS)} models): POST /v1beta/models/{{model}}:generateContent")
    for m in GEMINI_CHAT_MODELS:
        print(f"    - {m}")
    print(f"  Qwen Chat ({len(QWEN_CHAT_MODELS)} models): POST /api/v1/services/aigc/text-generation/generation")
    for m in QWEN_CHAT_MODELS:
        print(f"    - {m}")

    print(bold("\n── Embeddings ──"))
    for m in EMBEDDING_MODELS:
        print(f"    - {m}: POST /v1/embeddings")

    print(bold("\n── Audio ──"))
    for m in TTS_MODELS:
        print(f"    - {m}: POST /v1/audio/speech")
    print(f"    - whisper-1: POST /v1/audio/transcriptions")
    print(f"    - whisper-1: POST /v1/audio/translations")

    print(bold("\n── Image ──"))
    print(f"  OpenAI Image: POST /v1/images/generations, /v1/images/edits")
    print(f"    - gpt-image-2 [DOC ISSUE: 重复出现两次]")
    print(f"  Gemini Image: POST /v1beta/models/{{model}}:generateContent")
    for m in GEMINI_IMAGE_MODELS:
        print(f"    - {m}")
    print(f"  Qwen Image: POST /v1/images/generations, /v1/images/edits")
    for m in QWEN_IMAGE_GEN_MODELS + QWEN_IMAGE_EDIT_MODELS:
        print(f"    - {m}")

    print(bold("\n── Video (async) ──"))
    print(f"  所有视频 API: POST /v1/video/generations | GET /v1/video/generations/{{id}}")
    print(f"  Veo models:")
    for m in VEO_MODELS_DOC:
        print(f"    - {m}")
    print(f"  Wan models:")
    for m in WAN_MODELS_DOC:
        print(f"    - {m}")
    print(f"  SeeDance models:")
    for m in SEEDANCE_MODELS_DOC:
        print(f"    - {m}")

    print(bold("\n── Management ──"))
    endpoints = [
        ("public",  "GET /api/status"),
        ("public",  "GET /v1/models"),
        ("user",    "GET /api/user/self"),
        ("user",    "GET /api/token"),
        ("user",    "GET /api/log/self"),
        ("admin",   "GET /api/channel"),
        ("admin",   "GET /api/user"),
    ]
    for level, ep in endpoints:
        print(f"    [{level}] {ep}")

# ============================================================
# 主入口
# ============================================================
CATEGORIES = {
    "chat":       [run_openai_chat_tests, run_anthropic_tests, run_gemini_chat_tests, run_qwen_chat_tests],
    "embed":      [run_embedding_tests],
    "audio":      [run_audio_tests],
    "image":      [run_openai_image_tests, run_gemini_image_tests, run_qwen_image_tests],
    "video":      [run_video_tests],
    "management": [run_management_tests],
}

def main():
    parser = argparse.ArgumentParser(description="AI Router API 综合测试脚本")
    parser.add_argument("--category", "-c", choices=list(CATEGORIES.keys()),
                        help="只运行指定类别的测试")
    parser.add_argument("--list", "-l", action="store_true", help="列出所有测试项，不执行")
    args = parser.parse_args()

    if args.list:
        print_list()
        return

    if not API_KEY:
        print(red("错误: 请设置 API_KEY 环境变量"))
        print("  export API_KEY='your-api-key'")
        sys.exit(1)

    print(bold("AI Router API 综合测试"))
    print(f"  BASE_URL:       {BASE_URL}")
    print(f"  API_KEY:        {'*' * min(8, len(API_KEY)) + API_KEY[-4:] if len(API_KEY) > 4 else '***'}")
    print(f"  TEST_VIDEO:     {TEST_VIDEO}")
    print(f"  TEST_ALL_MODELS:{TEST_ALL_MODELS}")
    print(f"  开始时间:       {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if args.category:
        runners = CATEGORIES[args.category]
    else:
        runners = [fn for fns in CATEGORIES.values() for fn in fns]

    for runner in runners:
        try:
            runner()
        except Exception as e:
            print(red(f"\n[FATAL] {runner.__name__} 崩溃: {e}"))
            traceback.print_exc()

    print_summary()
    print(f"\n  结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
