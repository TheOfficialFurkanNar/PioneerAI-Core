# modules/task_router.py

from __future__ import annotations
import re
import os
import logging
import functools
import importlib
from pathlib import Path
from typing import List, Tuple

import openai
from config.settings import OPENAI_MODEL

# API anahtarını ortam değişkeninden oku
openai.api_key = os.getenv("OPENAI_API_KEY")

# ------------------------------------------------------------------ #
# 1. REGEX TABANLI KURAL SETİ (pattern, intent, weight)              #
# ------------------------------------------------------------------ #
_RULES: List[Tuple[re.Pattern, str, float]] = [
    (re.compile(r"(özet|summary|genel bakış|ne oldu)", re.I),   "summarize",  0.9),
    (re.compile(r"(sorun|çalışmıyor|hata|debug)", re.I),        "debug",      0.9),
    (re.compile(r"(proje|tasarım|mimari|architecture)", re.I),  "project",    0.8),
    (re.compile(r"(test|deneme|kontrol|simulate)", re.I),       "test",       0.8),
    (re.compile(r"(yardım|nasıl|açıklama|dokümantasyon)", re.I),"help",       0.7),
    (re.compile(r"(düşünce|felsefe|vizyon|etik)", re.I),        "philosophy", 0.7),
    (re.compile(r"(bellek|hafıza|bağlam|context)", re.I),       "context",    0.8),
    (re.compile(r"(ilham|üret|örnek|suggest)", re.I),           "creative",   0.7),
]
DEFAULT_INTENT: Tuple[str, float] = ("general", 0.5)

# ------------------------------------------------------------------ #
# 2. Kural Ekleme (Plugin Sistemi)                                   #
# ------------------------------------------------------------------ #
def _load_plugins(plugin_dir: str = "plugins") -> None:
    """
    Proje kökünde /plugins klasörüne bakar.
    İçindeki *.py dosyalarında INTENT_PLUGIN tanımı varsa _RULES'e ekler.
    """
    path = Path(plugin_dir)
    if not path.exists() or not path.is_dir():
        return

    for file in path.glob("*.py"):
        try:
            mod = importlib.import_module(f"{path.name}.{file.stem}")
            plugin_rules: List[Tuple[str, str, float]] = getattr(mod, "INTENT_PLUGIN", [])
            for pattern, intent, weight in plugin_rules:
                _RULES.append((re.compile(pattern, re.I), intent, weight))
            logging.info(f"[TaskRouter] Plugin yüklendi → {file.name}")
        except Exception as e:
            logging.warning(f"[TaskRouter] Plugin yüklenemedi ({file.name}): {e}")

# başta plugin'leri yükle
_load_plugins()

# ------------------------------------------------------------------ #
# 3. Regex Seçicisi (en yüksek ağırlık)                              #
# ------------------------------------------------------------------ #
@functools.lru_cache(maxsize=1024)
def _regex_intent(text: str) -> Tuple[str, float]:
    best: Tuple[str, float] = DEFAULT_INTENT
    for pattern, intent, weight in _RULES:
        if pattern.search(text) and weight > best[1]:
            best = (intent, weight)
    return best

# ------------------------------------------------------------------ #
# 4. GPT Tabanlı Yedek Sınıflandırıcı                                #
# ------------------------------------------------------------------ #
async def classify_via_gpt_async(
    text: str,
    model: str = OPENAI_MODEL
) -> Tuple[str, float]:
    prompt = (
        "You are an intent classifier. Return ONLY one of: "
        "summarize, debug, project, test, help, philosophy, "
        "context, creative, general.\n\n"
        f"Message: \"{text}\"\nIntent:"
    )
    resp = await openai.ChatCompletion.acreate(
        model=model,
        messages=[
            {"role": "system", "content": "Label intent."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=5,
        temperature=0.0
    )
    intent = resp.choices[0].message.content.strip().lower()
    return intent, 0.95

# ------------------------------------------------------------------ #
# 5. Senkron classify_intent Wrapper                                  #
# ------------------------------------------------------------------ #
def classify_intent(text: str) -> str:
    """
    Senkron classify_intent; sadece intent string’ini döner.
    """
    try:
        intent, _ = asyncio.run(route_intent(text, use_gpt_fallback=False))
    except Exception:
        intent, _ = asyncio.run(route_intent(text))
    return intent

# ------------------------------------------------------------------ #
# 6. Tek Giriş Noktası                                               #
# ------------------------------------------------------------------ #
async def route_intent(
    message: str,
    use_gpt_fallback: bool = True
) -> Tuple[str, float]:
    """
    • Önce regex tabanlı kuralları dener.
    • Confidence ≤ 0.7 ise ve use_gpt_fallback=True ise GPT fallback kullanır.
    • Döner: (intent, confidence)
    """
    text = message.lower()
    intent, conf = _regex_intent(text)

    if conf >= 0.7 or not use_gpt_fallback:
        return intent, conf

    try:
        return await classify_via_gpt_async(text)
    except Exception as e:
        logging.warning(f"[TaskRouter] GPT fallback hatası: {e}")
        return intent, conf

# ------------------------------------------------------------------ #
# 7. Çoklu Intent (sıralı)                                           #
# ------------------------------------------------------------------ #
def multi_intent(message: str, top_k: int = 3) -> List[str]:
    """
    Pattern ağırlığına göre en fazla top_k intent’i sıralı döner.
    """
    text = message.lower()
    matches = [(intent, w) for pat, intent, w in _RULES if pat.search(text)]
    matches.sort(key=lambda x: x[1], reverse=True)
    return [m[0] for m in matches[:top_k]] or ["general"]

# ------------------------------------------------------------------ #
# 8. CLI Test                                                        #
# ------------------------------------------------------------------ #
if __name__ == "__main__":
    import asyncio

    samples = [
        "Bu kodda hata alıyorum, debug edebilir misin?",
        "5+7 kaç eder?",
        "Projenin mimarisi hakkında genel bakış verir misin?",
        "Hava durumu nasıl?",
        "Bana yaratıcı bir hikaye üretebilir misin?"
    ]

    for s in samples:
        intent, conf = asyncio.run(route_intent(s))
        print(f"{s!r:60} → {intent:<10} ({conf:.2f})")