# modules/chat_client.py
import asyncio
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from openai import AsyncOpenAI
import os

from config.settings import (
    MAX_TOKENS, TEMPERATURE, FREQUENCY_PENALTY,
    PRESENCE_PENALTY, TOP_P, SYSTEM_PROMPT
)
from .error_handler import retry_with_backoff
from .token_counter import TokenCounter


@dataclass
class ChatMessage:
    role: str
    content: str


class AsyncChatClient:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.token_counter = TokenCounter()
        self.logger = logging.getLogger(__name__)

    def select_model(self, messages: List[ChatMessage]) -> str:
        """Smart model selection based on token count"""
        token_count = self.token_manager.count_messages_tokens(messages)
        return "gpt-4o" if token_count > 3000 else "gpt-3.5-turbo"

    @retry_with_backoff(max_retries=3)
    async def chat_completion(
            self,
            messages: List[ChatMessage],
            model: Optional[str] = None
    ) -> Tuple[str, bool]:
        """
        Async chat completion with retry logic
        Returns: (response_text, success_status)
        """
        try:
            if not model:
                model = self.select_model(messages)

            message_dicts = [{"role": msg.role, "content": msg.content} for msg in messages]

            response = await self.client.chat.completions.create(
                model=model,
                messages=message_dicts,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
                top_p=TOP_P,
                frequency_penalty=FREQUENCY_PENALTY,
                presence_penalty=PRESENCE_PENALTY
            )

            output = response.choices[0].message.content.strip()
            self.logger.info(f"Successful completion with model: {model}")
            return output, True

        except Exception as e:
            self.logger.error(f"Chat completion failed: {e}")
            return f"[HATA] Yanıt alınamadı: {str(e)}", False