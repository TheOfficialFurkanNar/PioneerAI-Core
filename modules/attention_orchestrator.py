# modules/attention_orchestrator.py

import asyncio
import logging
import time
import torch
import hashlib
from typing import List, Dict, Optional, Union, AsyncGenerator
from dataclasses import dataclass

from config.settings import (
    ATTENTION_MODE, HYBRID_MODE_THRESHOLD, CACHE_SIZE,
    EMBEDDING_DIM, ATTENTION_HEADS, SEQUENCE_LENGTH
)
from .chat_client import AsyncChatClient, ChatMessage
from .attention_layer import MultiHeadAttention, attention_cache
from .neural_core import AttentionModel
from .token_counter import TokenCounter


@dataclass
class AttentionResult:
    """Result from attention processing"""
    content: str
    confidence: float
    processing_time: float
    method: str  # "local", "openai", "hybrid"
    attention_weights: Optional[torch.Tensor] = None


class AttentionOrchestrator:
    """
    Orchestrates between local attention processing and OpenAI API
    
    Provides hybrid processing capabilities with intelligent routing
    """
    
    def __init__(self, vocab_size: int = 50000):
        self.openai_client = AsyncChatClient()
        self.token_counter = TokenCounter()
        self.logger = logging.getLogger(__name__)
        
        # Initialize local attention model if needed
        if ATTENTION_MODE in ["local", "hybrid"]:
            self.attention_model = AttentionModel(
                vocab_size=vocab_size,
                d_model=EMBEDDING_DIM,
                num_heads=ATTENTION_HEADS,
                max_seq_len=SEQUENCE_LENGTH
            )
            self.attention_model.eval()  # Set to evaluation mode
        else:
            self.attention_model = None
            
        # Simple tokenizer (in production, use proper tokenizer)
        self.vocab = self._build_simple_vocab()
        
    def _build_simple_vocab(self) -> Dict[str, int]:
        """Build a simple vocabulary for demonstration"""
        # In production, use a proper tokenizer like tiktoken or transformers
        vocab = {"<pad>": 0, "<unk>": 1, "<start>": 2, "<end>": 3}
        
        # Add common words (simplified for demo)
        common_words = [
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "up", "about", "into", "through", "during",
            "before", "after", "above", "below", "between", "among", "is", "are",
            "was", "were", "be", "been", "being", "have", "has", "had", "do", "does",
            "did", "will", "would", "could", "should", "may", "might", "must", "can",
            "hello", "hi", "how", "what", "when", "where", "why", "who", "which",
            "this", "that", "these", "those", "i", "you", "he", "she", "it", "we", "they"
        ]
        
        for i, word in enumerate(common_words, start=4):
            vocab[word] = i
            
        return vocab
        
    def _tokenize_text(self, text: str) -> List[int]:
        """Simple tokenization (replace with proper tokenizer in production)"""
        words = text.lower().split()
        tokens = []
        
        for word in words:
            # Remove punctuation
            word = ''.join(c for c in word if c.isalnum())
            token_id = self.vocab.get(word, self.vocab["<unk>"])
            tokens.append(token_id)
            
        return tokens
        
    def _create_cache_key(self, messages: List[ChatMessage]) -> str:
        """Create cache key for attention results"""
        content = " ".join([msg.content for msg in messages])
        return hashlib.md5(content.encode()).hexdigest()
        
    async def _process_with_local_attention(
        self, 
        messages: List[ChatMessage]
    ) -> AttentionResult:
        """Process messages using local attention model"""
        start_time = time.perf_counter()
        
        try:
            # Combine messages into single text
            combined_text = " ".join([msg.content for msg in messages])
            
            # Tokenize
            tokens = self._tokenize_text(combined_text)
            
            # Pad or truncate to sequence length
            if len(tokens) > SEQUENCE_LENGTH:
                tokens = tokens[:SEQUENCE_LENGTH]
            else:
                tokens.extend([0] * (SEQUENCE_LENGTH - len(tokens)))
                
            # Convert to tensor
            input_tensor = torch.tensor([tokens], dtype=torch.long)
            
            # Process with attention model
            with torch.no_grad():
                encodings = self.attention_model.encode_text(input_tensor)
                
            # Simple response generation (in production, use proper decoder)
            response = "Local attention processing completed successfully."
            confidence = 0.85  # Placeholder confidence
            
            processing_time = time.perf_counter() - start_time
            
            return AttentionResult(
                content=response,
                confidence=confidence,
                processing_time=processing_time,
                method="local"
            )
            
        except Exception as e:
            self.logger.error(f"Local attention processing failed: {e}")
            processing_time = time.perf_counter() - start_time
            
            return AttentionResult(
                content=f"Local processing error: {str(e)}",
                confidence=0.0,
                processing_time=processing_time,
                method="local"
            )
            
    async def _process_with_openai(
        self, 
        messages: List[ChatMessage]
    ) -> AttentionResult:
        """Process messages using OpenAI API"""
        start_time = time.perf_counter()
        
        try:
            response, success = await self.openai_client.chat_completion(messages)
            processing_time = time.perf_counter() - start_time
            
            return AttentionResult(
                content=response,
                confidence=0.95 if success else 0.0,
                processing_time=processing_time,
                method="openai"
            )
            
        except Exception as e:
            self.logger.error(f"OpenAI processing failed: {e}")
            processing_time = time.perf_counter() - start_time
            
            return AttentionResult(
                content=f"OpenAI processing error: {str(e)}",
                confidence=0.0,
                processing_time=processing_time,
                method="openai"
            )
            
    def _should_use_local_attention(self, messages: List[ChatMessage]) -> bool:
        """Determine whether to use local attention based on various factors"""
        
        # Check message complexity
        total_tokens = sum(len(msg.content.split()) for msg in messages)
        
        # Use local attention for shorter messages in hybrid mode
        if ATTENTION_MODE == "hybrid":
            return total_tokens < 100  # Threshold for local processing
            
        return ATTENTION_MODE == "local"
        
    async def process_messages(
        self, 
        messages: List[ChatMessage],
        use_cache: bool = True
    ) -> AttentionResult:
        """
        Process messages with intelligent routing between local and OpenAI
        
        Args:
            messages: List of chat messages to process
            use_cache: Whether to use attention caching
            
        Returns:
            AttentionResult with processed content and metadata
        """
        # Check cache first
        if use_cache and attention_cache:
            cache_key = self._create_cache_key(messages)
            cached_result = attention_cache.get(cache_key)
            if cached_result:
                self.logger.info("Using cached attention result")
                return cached_result
                
        # Determine processing method
        if ATTENTION_MODE == "openai":
            result = await self._process_with_openai(messages)
        elif ATTENTION_MODE == "local":
            result = await self._process_with_local_attention(messages)
        else:  # hybrid mode
            if self._should_use_local_attention(messages):
                result = await self._process_with_local_attention(messages)
                
                # Fallback to OpenAI if local confidence is too low
                if result.confidence < HYBRID_MODE_THRESHOLD:
                    self.logger.info("Local confidence low, falling back to OpenAI")
                    openai_result = await self._process_with_openai(messages)
                    
                    # Use OpenAI result if it has higher confidence
                    if openai_result.confidence > result.confidence:
                        result = openai_result
                        result.method = "hybrid"
            else:
                result = await self._process_with_openai(messages)
                
        # Cache the result
        if use_cache and attention_cache and result.confidence > 0.5:
            cache_key = self._create_cache_key(messages)
            attention_cache.put(cache_key, result)
            
        self.logger.info(
            f"Processed with {result.method} method, "
            f"confidence: {result.confidence:.2f}, "
            f"time: {result.processing_time:.2f}s"
        )
        
        return result
        
    async def stream_process_messages(
        self, 
        messages: List[ChatMessage]
    ) -> AsyncGenerator[str, None]:
        """
        Stream processing for real-time responses
        
        Args:
            messages: List of chat messages to process
            
        Yields:
            Streaming response chunks
        """
        try:
            # For now, process normally and yield the result
            # In production, implement proper streaming for local attention
            result = await self.process_messages(messages)
            
            # Simulate streaming by yielding chunks
            words = result.content.split()
            for i, word in enumerate(words):
                if i == 0:
                    yield word
                else:
                    yield f" {word}"
                    
                # Small delay to simulate streaming
                await asyncio.sleep(0.05)
                
        except Exception as e:
            self.logger.error(f"Stream processing failed: {e}")
            yield f"[Stream Error: {str(e)}]"
            
    def get_model_info(self) -> Dict[str, any]:
        """Get information about the attention model"""
        info = {
            "attention_mode": ATTENTION_MODE,
            "embedding_dim": EMBEDDING_DIM,
            "attention_heads": ATTENTION_HEADS,
            "sequence_length": SEQUENCE_LENGTH,
            "cache_enabled": attention_cache is not None,
            "local_model_loaded": self.attention_model is not None
        }
        
        if self.attention_model:
            info["model_parameters"] = sum(
                p.numel() for p in self.attention_model.parameters()
            )
            
        return info
        
    def clear_cache(self):
        """Clear attention cache"""
        if attention_cache:
            attention_cache.clear()
            self.logger.info("Attention cache cleared")


# Global orchestrator instance
attention_orchestrator = AttentionOrchestrator()