# orchestrator.py

import time
import logging
import asyncio
from typing import AsyncGenerator

from modules.summarizer_agent import SummarizerAgent
from modules.attention_orchestrator import attention_orchestrator
from modules.chat_client import ChatMessage
from config.settings import ATTENTION_MODE

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


# ------------------------------------------------------------
# 3. Attention-Enhanced Message Handling
# ------------------------------------------------------------
async def handle_attention_message(user_id: str, message: str) -> dict:
    """Handle message with attention mechanism"""
    start = time.perf_counter()
    try:
        # Create chat message
        chat_message = ChatMessage(role="user", content=message)
        
        # Process with attention orchestrator
        result = await attention_orchestrator.process_messages([chat_message])
        
        latency = round(time.perf_counter() - start, 2)
        
        logging.info(
            f"[Orch] 🧠 Attention | method={result.method} | "
            f"confidence={result.confidence:.2f} | latency={latency}s"
        )
        
        return {
            "reply": result.content,
            "meta": {
                "method": result.method,
                "confidence": result.confidence,
                "processing_time": result.processing_time,
                "latency": latency,
                "user_id": user_id
            }
        }
        
    except Exception as e:
        logging.exception("[Orch] 🚨 Attention processing error")
        return {"reply": f"🚨 Attention Error: {e}", "meta": {}}


async def handle_hybrid_message(user_id: str, message: str) -> dict:
    """Handle message with hybrid attention + summarization"""
    start = time.perf_counter()
    try:
        # First, try attention processing
        chat_message = ChatMessage(role="user", content=message)
        attention_result = await attention_orchestrator.process_messages([chat_message])
        
        # If attention confidence is high, use it directly
        if attention_result.confidence > 0.8:
            latency = round(time.perf_counter() - start, 2)
            
            logging.info(
                f"[Orch] 🔥 Hybrid-Attention | confidence={attention_result.confidence:.2f} | "
                f"latency={latency}s"
            )
            
            return {
                "reply": attention_result.content,
                "meta": {
                    "method": "hybrid-attention",
                    "confidence": attention_result.confidence,
                    "processing_time": attention_result.processing_time,
                    "latency": latency,
                    "user_id": user_id
                }
            }
        
        # Otherwise, fall back to summarization
        else:
            logging.info(f"[Orch] 🔄 Falling back to summarization (confidence: {attention_result.confidence:.2f})")
            
            style = "brief"
            reply = await summarizer.generate_summary(
                user_id=user_id,
                message=message,
                style=style
            )
            
            latency = round(time.perf_counter() - start, 2)
            
            logging.info(f"[Orch] 🔥 Hybrid-Summary | style={style} | latency={latency}s")
            
            return {
                "reply": reply,
                "meta": {
                    "method": "hybrid-summary",
                    "style": style,
                    "attention_confidence": attention_result.confidence,
                    "latency": latency,
                    "user_id": user_id
                }
            }
            
    except Exception as e:
        logging.exception("[Orch] 🚨 Hybrid processing error")
        return {"reply": f"🚨 Hybrid Error: {e}", "meta": {}}


async def handle_stream_attention_message(
    user_id: str,
    message: str
) -> AsyncGenerator[str, None]:
    """Stream attention-enhanced responses"""
    try:
        chat_message = ChatMessage(role="user", content=message)
        
        async for chunk in attention_orchestrator.stream_process_messages([chat_message]):
            yield chunk
            
    except Exception as e:
        logging.exception("[Orch] 🔴 Stream attention error")
        yield f"[Stream Attention Error: {e}]"


def get_attention_info() -> dict:
    """Get information about attention system"""
    return attention_orchestrator.get_model_info()


def clear_attention_cache():
    """Clear attention cache"""
    attention_orchestrator.clear_cache()