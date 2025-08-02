# modules/memory_manager.py
import asyncio
import json
import aiofiles
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import deque
import logging

from config.settings import MEMORY_JSON, MEMORY_TXT, ENCODING


@dataclass
class ConversationTurn:
    user: str
    bot: str
    timestamp: str
    intent: Optional[str] = None
    confidence: Optional[float] = None
    model_used: Optional[str] = None


class AsyncMemoryManager:
    def __init__(self, max_history: int = 20):
        self.conversation_history = deque(maxlen=max_history)
        self.pending_writes: List[ConversationTurn] = []
        self.write_buffer_size = 5  # Write every 5 turns
        self.logger = logging.getLogger(__name__)
        self._write_lock = asyncio.Lock()

    async def load_memory(self) -> bool:
        """Load conversation history from persistent storage"""
        try:
            async with aiofiles.open(MEMORY_JSON, "r", encoding=ENCODING) as f:
                content = await f.read()
                data = json.loads(content) if content else {"conversation": []}

                for turn_data in data.get("conversation", []):
                    turn = ConversationTurn(**turn_data)
                    self.conversation_history.append(turn)

                self.logger.info(f"Loaded {len(self.conversation_history)} conversation turns")
                return True

        except Exception as e:
            self.logger.warning(f"Could not load memory: {e}")
            return False

    def add_turn(self, user_input: str, bot_response: str,
                 intent: Optional[str] = None, confidence: Optional[float] = None,
                 model_used: Optional[str] = None):
        """Add new conversation turn to memory"""
        turn = ConversationTurn(
            user=user_input,
            bot=bot_response,
            timestamp=datetime.now().isoformat(),
            intent=intent,
            confidence=confidence,
            model_used=model_used
        )

        self.conversation_history.append(turn)
        self.pending_writes.append(turn)

        # Auto-flush if buffer is full
        if len(self.pending_writes) >= self.write_buffer_size:
            asyncio.create_task(self.flush_to_disk())

    async def flush_to_disk(self):
        """Write buffered turns to persistent storage"""
        if not self.pending_writes:
            return

        async with self._write_lock:
            try:
                # Read existing data
                try:
                    async with aiofiles.open(MEMORY_JSON, "r", encoding=ENCODING) as f:
                        content = await f.read()
                        data = json.loads(content) if content else {"conversation": []}
                except:
                    data = {"conversation": []}

                # Add pending writes
                for turn in self.pending_writes:
                    data["conversation"].append(asdict(turn))

                # Write back to file
                async with aiofiles.open(MEMORY_JSON, "w", encoding=ENCODING) as f:
                    await f.write(json.dumps(data, ensure_ascii=False, indent=2))

                # Also write to text file
                async with aiofiles.open(MEMORY_TXT, "a", encoding=ENCODING) as f:
                    for turn in self.pending_writes:
                        await f.write(f"USER: {turn.user}\nBOT: {turn.bot}\n\n")

                self.logger.info(f"Flushed {len(self.pending_writes)} turns to disk")
                self.pending_writes.clear()

            except Exception as e:
                self.logger.error(f"Failed to flush memory to disk: {e}")

    def get_recent_messages(self, limit: int = 10) -> List[Dict[str, str]]:
        """Get recent conversation for context"""
        recent = list(self.conversation_history)[-limit:]
        return [{"user": turn.user, "bot": turn.bot} for turn in recent]

    def clear_memory(self):
        """Clear conversation history"""
        self.conversation_history.clear()
        self.pending_writes.clear()
        self.logger.info("Memory cleared")