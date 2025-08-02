# modules/token_counter.py

import tiktoken
from functools import lru_cache
from typing import List, Dict
from .chat_client import ChatMessage

class TokenCounter:
    """
    Efficiently counts OpenAI tokens for text and message lists,
    with caching, per-message overhead, dynamic model support, and fallback.
    """
    def __init__(self):
        # Prepare encoders once
        self.encoders: Dict[str, tiktoken.Encoding] = {}
        self.default_encoder = tiktoken.get_encoding("cl100k_base")

        # Register known model aliases
        for alias, model_name in [
            ("gpt-4o", "gpt-4o"),
            ("gpt-4", "gpt-4o"),
            ("gpt-3.5-turbo", "gpt-3.5-turbo"),
        ]:
            try:
                self.encoders[alias] = tiktoken.encoding_for_model(model_name)
            except KeyError:
                self.encoders[alias] = self.default_encoder

    @lru_cache(maxsize=512)
    def _get_encoder(self, model: str) -> tiktoken.Encoding:
        return self.encoders.get(model, self.default_encoder)

    def count_messages_tokens(self, messages: List[ChatMessage], model: str = "gpt-4o") -> int:
        """
        Count tokens for a list of ChatMessage objects, including OpenAI overhead:
          - 4 tokens per message
          - +2 tokens if message.name is present
          - +2 tokens for assistant reply start
        """
        encoder = self._get_encoder(model)
        total = 0

        for msg in messages:
            overhead = 4 + (2 if getattr(msg, "name", None) else 0)
            total += overhead + len(encoder.encode(msg.content))

        # Add tokens for the reply start (per OpenAI spec)
        total += 2
        return total

    @lru_cache(maxsize=512)
    def count_text_tokens(self, text: str, model: str = "gpt-4o") -> int:
        """Count tokens for a single text string."""
        encoder = self._get_encoder(model)
        return len(encoder.encode(text))