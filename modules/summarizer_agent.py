# modules/summarizer_agent.py

import os
import hashlib
import importlib
import pkgutil
import asyncio
import time
import logging
from typing import Literal, Dict, AsyncGenerator

from openai import AsyncOpenAI

# OpenAI exceptions
try:
    from openai import OpenAIError
except ImportError:
    try:
        from openai._exceptions import OpenAIError
    except ImportError:
        OpenAIError = Exception
        logging.warning(
            "[SummarizerAgent] OpenAI exceptions bulunamadı, Exception fallback kullanılıyor."
        )

# Diskcache importu; yoksa in-memory fallback
try:
    from diskcache import Cache
except ImportError:
    Cache = None
    logging.warning(
        "[SummarizerAgent] 'diskcache' bulunamadı, in-memory cache kullanılıyor."
    )

from config.settings import OPENAI_MODEL, SUMMARY_TIMEOUT, MEMORY_JSON
from modules.memory_analyzer import MemoryAnalyzer
from modules.task_router import route_intent

# ------------------------------------------------------------
# 0. Plugin Tabanlı Stil Yükleyici
# ------------------------------------------------------------
STYLE_TEMPLATES: Dict[str, str] = {
    "brief": (
        "Aşağıdaki bağlam ve intent’e göre kullanıcı mesajını "
        "kısa ve öz bir şekilde özetle."
    )
}

def _load_style_plugins():
    pkg_name = __name__.rsplit('.', 1)[0] + ".summary_styles"
    try:
        package = importlib.import_module(pkg_name)
    except ModuleNotFoundError:
        return

    for finder, name, is_pkg in pkgutil.iter_modules(package.__path__):
        module = importlib.import_module(f"{pkg_name}.{name}")
        tpl = getattr(module, "STYLE_TEMPLATE", None)
        if isinstance(tpl, dict):
            STYLE_TEMPLATES.update(tpl)

_load_style_plugins()

# ------------------------------------------------------------
# 1. DiskCache ile Özet Cache’i
# ------------------------------------------------------------
CACHE_DIR = os.getenv("SUMMARY_CACHE_DIR", ".summary_cache")
if Cache:
    cache = Cache(CACHE_DIR)
else:
    cache: Dict[str, tuple[str, float]] = {}

def _make_cache_key(user_id: str, message: str, style: str) -> str:
    digest = hashlib.sha256(f"{user_id}|{style}|{message}".encode()).hexdigest()
    return f"summary:{digest}"

# ------------------------------------------------------------
# 2. SummarizerAgent Sınıfı
# ------------------------------------------------------------
class SummarizerAgent:
    def __init__(
        self,
        memory_path: str = MEMORY_JSON,
        model: str = OPENAI_MODEL,
        timeout: int = SUMMARY_TIMEOUT
    ):
        self.mem_analyzer = MemoryAnalyzer(memory_path=memory_path)
        self.model = model
        self.timeout = timeout
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def generate_summary(
        self,
        user_id: str,
        message: str,
        style: Literal["brief", "deep", "bullet", "technical", "story"] = "brief"
    ) -> str:
        key = _make_cache_key(user_id, message, style)
        # Cache kontrolü
        if Cache:
            val = cache.get(key)
            if val is not None:
                return val
        else:
            entry = cache.get(key)
            if entry and (time.time() - entry[1] < self.timeout):
                return entry[0]

        report = self.mem_analyzer(
            analyze_intent=True,
            analyze_activity=False
        )
        context = "\n".join(f"- {k}: {v}"
                             for k, v in report["report"]["top_keywords"])
        intent, _ = await route_intent(message, use_gpt_fallback=False)

        instruction = STYLE_TEMPLATES.get(style, STYLE_TEMPLATES["brief"])
        prompt = (
            f"{instruction}\n\n"
            f"Bağlam:\n{context}\n\n"
            f"Intent: {intent}\n\n"
            f"Mesaj: {message}\n\n"
            f"Özet:"
        )

        try:
            resp = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful summarizer."},
                        {"role": "user",   "content": prompt}
                    ],
                    temperature=0.2,
                    max_tokens=300
                ),
                timeout=self.timeout
            )
            summary = resp.choices[0].message.content.strip()

        except asyncio.TimeoutError:
            summary = self._fallback_summary(message)

        except OpenAIError as oe:
            logging.error(f"[SummarizerAgent] OpenAI hata: {oe}")
            summary = f"[Özet hatası: {oe}]"

        # Cache’e kaydet
        if Cache:
            cache.set(key, summary, expire=self.timeout)
        else:
            cache[key] = (summary, time.time())

        return summary

    async def stream_summary(
        self,
        user_id: str,
        message: str,
        style: Literal["brief", "deep", "bullet", "technical", "story"] = "brief"
    ) -> AsyncGenerator[str, None]:
        report = self.mem_analyzer(
            analyze_intent=True,
            analyze_activity=False
        )
        context = "\n".join(f"- {k}: {v}"
                             for k, v in report["report"]["top_keywords"])
        intent, _ = await route_intent(message, use_gpt_fallback=False)
        instruction = STYLE_TEMPLATES.get(style, STYLE_TEMPLATES["brief"])

        prompt = (
            f"{instruction}\n\n"
            f"Bağlam:\n{context}\n\n"
            f"Intent: {intent}\n\n"
            f"Mesaj: {message}\n\n"
            f"Özet:"
        )

        try:
            resp = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful summarizer."},
                        {"role": "user",   "content": prompt}
                    ],
                    temperature=0.2,
                    max_tokens=500,
                    stream=True
                ),
                timeout=self.timeout
            )

            async for chunk in resp:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except asyncio.TimeoutError:
            yield self._fallback_summary(message)

        except OpenAIError as oe:
            logging.error(f"[SummarizerAgent] OpenAI hata: {oe}")
            yield f"[Özet hatası: {oe}]"

    def _fallback_summary(self, text: str, sentence_count: int = 3) -> str:
        sentences = text.replace("\n", " ").split(". ")
        return ". ".join(sentences[:sentence_count]).strip() + "."

# ------------------------------------------------------------
# 3. Basit Test Harness
# ------------------------------------------------------------
if __name__ == "__main__":
    import asyncio

    async def _test():
        agent = SummarizerAgent()
        user = "user123"
        msg = (
            "PioneerAI mimarisi hem modüler hem de web ve JS tarafıyla entegre. "
            "Özetleme, streaming ve cache destekli olacak şekilde yeniden yapılandırıldı."
        )

        print(">>> Brief Özet:")
        print(await agent.generate_summary(user, msg, style="brief"))

        print("\n>>> Bullet Özet:")
        print(await agent.generate_summary(user, msg, style="bullet"))

        print("\n>>> Streamed Özet:")
        async for part in agent.stream_summary(user, msg, style="deep"):
            print(part, end="")
    asyncio.run(_test())