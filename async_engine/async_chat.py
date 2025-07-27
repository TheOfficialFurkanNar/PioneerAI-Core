# async_engine/async_chat.py

import os
import re
import json
import logging
import asyncio
from typing import Optional, AsyncGenerator, Dict

import aiohttp
from dotenv import load_dotenv

from modules.memory_manager import get_user_conversation
from modules.memory_analyzer import MemoryAnalyzer
from modules.task_router import route_intent
from utils.tokens import count_tokens
from utils.cache import async_ttl_cache
from config.settings import (
    OPENAI_API_URL,
    OPENAI_MODEL,
    OPENAI_MODEL_STREAM,
    HTTP_TIMEOUT
)

# .env’den API anahtarını ve isteğe bağlı URL’i oku
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL = os.getenv("OPENAI_API_URL", OPENAI_API_URL)
TIMEOUT_SEC = int(os.getenv("HTTP_TIMEOUT", HTTP_TIMEOUT))

# 🔐 Güvenli JSON parse
def parse_json_safe(raw: str) -> Optional[Dict]:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        logging.warning(f"[async_chat] JSON parse hatası: {raw}")
        return None

# 🧼 XSS + küfür temizliği
def sanitize_output(text: str) -> str:
    text = re.sub(r"<.*?>", "", text)
    text = re.sub(r"\b(fuck|shit|bitch|asshole)\b", "***", text, flags=re.IGNORECASE)
    return text.strip()

# ------------------------------------------------------------
# Streaming yanıt üretici
# ------------------------------------------------------------
async def stream_response(
    system_prompt: str,
    user_message: str,
    temperature: float = 0.7,
    context_tokens: int = 0
) -> AsyncGenerator[str, None]:
    model = OPENAI_MODEL_STREAM if context_tokens > 3000 else OPENAI_MODEL

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message}
        ],
        "temperature": temperature,
        "stream": True,
        "max_tokens": 1500
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    timeout = aiohttp.ClientTimeout(total=TIMEOUT_SEC)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(OPENAI_API_URL, headers=headers, json=payload) as resp:
            logging.info(f"[async_chat] stream_response status={resp.status}")
            if resp.status != 200:
                yield f"[Stream Error: {resp.status}]"
                return

            async for line in resp.content:
                if not line:
                    continue
                chunk = line.decode("utf-8").strip()
                if not chunk.startswith("data: "):
                    continue
                piece = chunk.removeprefix("data: ").strip()
                if piece == "[DONE]":
                    break
                parsed = parse_json_safe(piece)
                if not parsed:
                    continue
                delta = parsed["choices"][0]["delta"].get("content", "")
                if delta:
                    yield sanitize_output(delta)

# ------------------------------------------------------------
# Non-streaming yanıt üretici
# ------------------------------------------------------------
async def generate_response(
    system_prompt: str,
    user_message: str,
    temperature: float = 0.7,
    context_tokens: int = 0
) -> Optional[str]:
    model = OPENAI_MODEL_STREAM if context_tokens > 3000 else OPENAI_MODEL

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message}
        ],
        "temperature": temperature,
        "max_tokens": 1500,
        "stream": False
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    timeout = aiohttp.ClientTimeout(total=TIMEOUT_SEC)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(OPENAI_API_URL, headers=headers, json=payload) as resp:
                if resp.status != 200:
                    logging.warning(f"[async_chat] generate_response status={resp.status}")
                    return None
                data = await resp.json()
                content = data["choices"][0]["message"]["content"]
                return sanitize_output(content)
    except Exception as e:
        logging.error(f"[async_chat] generate_response hata: {e}")
        return None

# ------------------------------------------------------------
# Yüksek seviyeli async_chat fonksiyonu
# ------------------------------------------------------------
@async_ttl_cache(ttl=60)
async def async_chat(
    user_id: str,
    user_message: str,
    temperature: float = 0.7
) -> AsyncGenerator[str, None]:
    """
    1. Kullanıcının önceki geçmişini DB’den çek
    2. MemoryAnalyzer ile hızlı analiz
    3. route_intent ile intent belirle
    4. Streaming veya non-stream seçimli yanıt üret
    """
    # 1️⃣ Geçmişi çek
    conv = await get_user_conversation(user_id)

    # 2️⃣ Analizci’yi hazırla
    analyzer = MemoryAnalyzer(memory_path="", intent_fn=None, summary_fn=None)
    analyzer.conversations = conv
    tokens = await asyncio.to_thread(lambda: count_tokens("".join(
        f"{t['user']}{t['bot']}" for t in conv[-8:]
    )))

    # 3️⃣ Intent’e göre sistem prompt’ı oluştur
    intent, _ = await route_intent(user_message)
    system_prompt = f"Intent: {intent}\nGeçmiş: {len(conv)} tur\n"

    # 4️⃣ Yanıtı stream et
    async for piece in stream_response(system_prompt, user_message, temperature, tokens):
        yield piece