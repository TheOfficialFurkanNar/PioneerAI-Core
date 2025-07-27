# orchestrator.py

import time
import logging
import asyncio
from typing import AsyncGenerator

from modules.summarizer_agent import SummarizerAgent

summarizer = SummarizerAgent()


# ------------------------------------------------------------
# 1. Standard Özetleyici (tek yanıt)
# ------------------------------------------------------------
async def handle_standard_message(user_id: str, message: str) -> dict:
    start = time.perf_counter()
    try:
        # Stil belirleme: dinamik ya da sabit
        style = "brief"
        reply = await summarizer.generate_summary(
            user_id=user_id,
            message=message,
            style=style
        )
        latency = round(time.perf_counter() - start, 2)

        logging.info(f"[Orch] 🧠 Standard | style={style} | latency={latency}s")

        return {
            "reply": reply,
            "meta": {
                "style": style,
                "latency": latency,
                "user_id": user_id
            }
        }

    except asyncio.TimeoutError:
        return {"reply": "⏱️ Zaman aşımı oluştu.", "meta": {}}

    except Exception as e:
        logging.exception("[Orch] 🚨 Beklenmeyen hata")
        return {"reply": f"🚨 Hata: {e}", "meta": {}}


# ------------------------------------------------------------
# 2. Akışlı Özetleyici (stream yanıt)
# ------------------------------------------------------------
async def handle_stream_message(
    user_id: str,
    message: str,
    style: str = "brief"
) -> AsyncGenerator[str, None]:
    try:
        async for chunk in summarizer.stream_summary(
            user_id=user_id,
            message=message,
            style=style
        ):
            yield chunk

    except Exception as e:
        logging.exception("[Orch] 🔴 Stream hatası")
        yield f"[Stream hatası: {e}]"