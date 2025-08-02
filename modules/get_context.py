# modules/get_context.py

import asyncio
import logging
import openai
from typing import Dict, Any, List

from modules.memory_analyzer import MemoryAnalyzer
from modules.memory_manager import (
    get_user_conversation,
    get_cache,
    set_cache
)
from modules.token_counter import count_tokens
from utils.cache_manager import async_ttl_cache
from config.settings import MAX_CONTEXT_TOKENS, MODEL_NAME, SYSTEM_PROMPT

@async_ttl_cache(ttl=60)  # Son 60 saniyelik çağrıları iç bellekte önbellekler
async def get_context_for_user(user_id: str) -> Dict[str, Any]:
    """
    Bellekten kullanıcının konuşma geçmişini alıp analiz ederek
    GPT için zengin bir bağlam döndürür. Ayrıca sonucu Redis'te
    kalıcı cache’e yazar.
    """

    # 0️⃣ Kalıcı Redis cache kontrolü
    cache_key = f"context_{user_id}"
    cached = get_cache(cache_key)
    if isinstance(cached, dict):
        logging.debug(f"[Context] Redis cache'ten çekildi: {cache_key}")
        return cached

    # 1️⃣ Konuşma geçmişini al
    user_conv: List[Dict[str, str]] = await get_user_conversation(user_id)

    # 2️⃣ MemoryAnalyzer'ı hazırla
    analyzer = MemoryAnalyzer(
        memory_path="",    # summary_fn kullanmıyoruz
        intent_fn=None,
        summary_fn=None
    )
    analyzer.conversations = user_conv

    # 3️⃣ CPU-bound işlemleri thread havuzunda çalıştır
    await asyncio.to_thread(analyzer.extract_keywords)
    await asyncio.to_thread(analyzer.analyze_tone)
    await asyncio.to_thread(analyzer.analyze_intents)

    # 4️⃣ Son 8 dönüşümü GPT ile özetle
    recent = user_conv[-8:]
    text_block = "\n".join(
        f"You: {t['user']}\nBot: {t.get('bot','')}"
        for t in recent
    )
    prompt = (
        "Aşağıdaki konuşmayı 3–4 anlamlı cümle ile özetle:\n"
        + text_block
    )
    resp = await openai.ChatCompletion.acreate(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt}
        ]
    )
    summary = resp.choices[0].message.content

    # 5️⃣ Token limiti aşılırsa özet budanır
    preview = f"{summary}\nTone: {analyzer.tone_stats}\nIntents: {dict(analyzer.intent_stats)}"
    if count_tokens(preview) > MAX_CONTEXT_TOKENS:
        summary = summary[:600] + "…"
        logging.info("[Context] GPT bağlamı budandı.")

    # 6️⃣ En baskın intent ve örnek mesajlar
    top = analyzer.intent_stats.most_common(1)
    primary = top[0][0] if top else "general"
    examples = analyzer.intent_examples.get(primary, [])[:2]

    # 7️⃣ Bağlam verisini paketle
    context_data: Dict[str, Any] = {
        "summary": summary,
        "tone": analyzer.tone_stats,
        "intents": analyzer.intent_stats.most_common(3),
        "top_keywords": analyzer.keywords.most_common(6),
        "primary_intent": primary,
        "example_messages": examples
    }

    # 8️⃣ Sonucu Redis cache’e yaz
    set_cache(cache_key, context_data)
    logging.debug(f"[Context] Redis cache’e yazıldı: {cache_key}")

    return context_data