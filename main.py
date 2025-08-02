# main.py - PioneerAI v2.0 - Modern Async Architecture
import asyncio
import logging
import os
import time
from typing import Optional, List, Dict
from datetime import datetime

from modules.error_handler import ErrorHandler, retry_with_backoff
from modules.token_counter import TokenCounter
from modules.chat_client import AsyncChatClient, ChatMessage
from modules.memory_manager import AsyncMemoryManager
from modules.task_router import classify_intent

from config.settings import (
    SYSTEM_PROMPT, SESSION_TIMEOUT, MAX_TOKENS, TEMPERATURE,
    FREQUENCY_PENALTY, PRESENCE_PENALTY, TOP_P
)


class PioneerAI:
    """
    Main PioneerAI application orchestrator.
    Integrates all modules for professional-grade AI chat system.
    """

    def __init__(self):
        # Initialize error handling first
        self.error_handler = ErrorHandler()
        self.error_handler.setup_logging("INFO")
        self.logger = logging.getLogger(__name__)

        # Initialize core modules
        self.token_counter = TokenCounter()
        self.chat_client = AsyncChatClient(self.token_counter)
        self.memory_manager = AsyncMemoryManager(max_history=20)

        # Session management
        self.last_input_time = time.time()
        self.session_active = True

        self.logger.info("🧠 PioneerAI v2.0 initialized with modern async architecture")

    async def initialize(self) -> bool:
        """Initialize the application and load persistent data"""
        try:
            success = await self.memory_manager.load_memory()
            if success:
                self.logger.info("Memory loaded successfully")
            else:
                self.logger.warning("Failed to load memory, starting fresh")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize PioneerAI: {e}")
            return False

    def _prepare_messages(self, user_input: str) -> List[ChatMessage]:
        """Prepare message list for OpenAI API"""
        messages = [ChatMessage(role="system", content=SYSTEM_PROMPT)]

        # Add conversation history
        recent_history = self.memory_manager.get_recent_messages(limit=10)
        for turn in recent_history:
            messages.append(ChatMessage(role="user", content=turn["user"]))
            messages.append(ChatMessage(role="assistant", content=turn["bot"]))

        # Add current user input
        messages.append(ChatMessage(role="user", content=user_input))

        return messages

    def _handle_special_commands(self, user_input: str) -> Optional[str]:
        """Handle special commands like !clear, !help, etc."""
        command = user_input.strip().lower()

        if command.startswith("!clear"):
            self.memory_manager.clear_memory()
            self.logger.info("Memory cleared by user command")
            return "🧼 Hafıza temizlendi."

        elif command.startswith("!help"):
            return self._get_help_message()

        elif command.startswith("!stats"):
            return self._get_stats_message()

        return None

    def _get_help_message(self) -> str:
        """Generate help message"""
        return """
🚀 PioneerAI v2.0 - Komutlar:
• !clear - Hafızayı temizle
• !help - Bu yardım mesajını göster
• !stats - Oturum istatistikleri
• quit/exit/bye - Çıkış yap
        """.strip()

    def _get_stats_message(self) -> str:
        """Generate session statistics"""
        history_count = len(self.memory_manager.conversation_history)
        session_duration = time.time() - (self.last_input_time - SESSION_TIMEOUT + 60)  # Approximate

        return f"""
📊 Oturum İstatistikleri:
• Konuşma geçmişi: {history_count} mesaj
• Oturum süresi: {session_duration / 60:.1f} dakika
• Bellek durumu: {'Aktif' if history_count > 0 else 'Boş'}
        """.strip()

    @retry_with_backoff(max_retries=3, base_delay=1.0, max_delay=30.0)
    async def _get_ai_response(self, messages: List[ChatMessage]) -> tuple[str, bool, str]:
        """Get response from OpenAI with retry logic"""
        try:
            # Log token usage for cost tracking
            token_count = self.token_counter.count_messages_tokens(messages)
            model = "gpt-4o" if token_count > 3000 else "gpt-3.5-turbo"

            self.logger.info(f"Processing request with {token_count} tokens using {model}")

            response, success = await self.chat_client.chat_completion(messages, model)

            if success:
                self.logger.info(f"Successfully generated response using {model}")
            else:
                self.logger.warning(f"Failed to generate response, using fallback")

            return response, success, model

        except Exception as e:
            self.logger.error(f"Unexpected error in AI response generation: {e}")
            return f"[HATA] Beklenmeyen hata: {str(e)}", False, "unknown"

    async def process_user_input(self, user_input: str) -> str:
        """Process user input and generate response"""
        try:
            # Update session timing
            self.last_input_time = time.time()

            # Handle special commands
            special_response = self._handle_special_commands(user_input)
            if special_response:
                return special_response

            # Classify intent for potential routing
            intent = classify_intent(user_input)
            self.logger.debug(f"Classified intent: {intent}")

            # Prepare messages for AI
            messages = self._prepare_messages(user_input)

            # Get AI response
            bot_response, success, model_used = await self._get_ai_response(messages)

            # Store in memory
            self.memory_manager.add_turn(
                user_input=user_input,
                bot_response=bot_response,
                intent=intent,
                confidence=0.95 if success else 0.5,
                model_used=model_used
            )

            return bot_response

        except Exception as e:
            self.logger.error(f"Error processing user input: {e}")
            return f"[SISTEM HATASI] Giriş işlenirken hata oluştu: {str(e)}"

    def check_session_timeout(self) -> bool:
        """Check if session has timed out"""
        if time.time() - self.last_input_time > SESSION_TIMEOUT:
            self.logger.info("Session timed out")
            return True
        return False

    async def cleanup(self):
        """Cleanup resources before shutdown"""
        try:
            await self.memory_manager.flush_to_disk()
            self.logger.info("Successfully flushed memory to disk")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    async def run_interactive_session(self):
        """Run the main interactive chat loop"""
        print("🧠 PioneerAI v2.0 başlatıldı – Modern async architecture aktif!")
        print("💡 Komutlar için !help yazın")

        try:
            while self.session_active:
                # Check session timeout
                if self.check_session_timeout():
                    print("⏳ Oturum süresi doldu. Güvenlik nedeniyle çıkış yapılıyor.")
                    break

                try:
                    user_input = input("\n🚀 You: ")

                    # Handle exit commands
                    if user_input.strip().lower() in ["quit", "exit", "bye"]:
                        print("🤖 Chatbot: Görüşmek üzere komutan! 🚀")
                        break

                    if not user_input.strip():
                        continue

                    # Process input and get response
                    response = await self.process_user_input(user_input)
                    print(f"🤖 PioneerAI: {response}")

                except (KeyboardInterrupt, EOFError):
                    print("\n🚪 Çıkış yapılıyor...")
                    break
                except Exception as e:
                    self.logger.error(f"Error in interactive loop: {e}")
                    print(f"[HATA] Beklenmeyen hata: {e}")

        finally:
            await self.cleanup()


# Enhanced Chat Client Integration
class AsyncChatClient:
    """Modern OpenAI client with your TokenCounter integration"""

    def __init__(self, token_counter: TokenCounter):
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        except ImportError:
            raise ImportError("Please install openai>=1.0.0: pip install openai>=1.0.0")

        self.token_counter = token_counter
        self.logger = logging.getLogger(__name__)

    def select_model(self, messages: List[ChatMessage]) -> str:
        """Smart model selection based on token count using your TokenCounter"""
        token_count = self.token_counter.count_messages_tokens(messages)
        return "gpt-4o" if token_count > 3000 else "gpt-3.5-turbo"

    @retry_with_backoff(max_retries=3)
    async def chat_completion(
            self,
            messages: List[ChatMessage],
            model: Optional[str] = None
    ) -> tuple[str, bool]:
        """Modern OpenAI API call with your error handling"""
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
        return output, True


async def main():
    """Main application entry point"""
    pioneer_ai = PioneerAI()

    # Initialize the application
    if not await pioneer_ai.initialize():
        print("❌ PioneerAI başlatılamadı!")
        return

    # Run interactive session
    await pioneer_ai.run_interactive_session()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 PioneerAI kapatıldı.")
    except Exception as e:
        print(f"❌ Kritik hata: {e}")