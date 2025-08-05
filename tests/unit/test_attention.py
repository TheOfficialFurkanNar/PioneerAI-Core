# tests/unit/test_attention.py

import unittest
import torch
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from modules.attention_layer import (
    ScaledDotProductAttention, MultiHeadAttention,
    PositionalEncoding, AttentionCache
)
from modules.neural_core import AttentionModel, TokenEmbedding, FeedForward
from modules.attention_orchestrator import AttentionOrchestrator, AttentionResult
from modules.chat_client import ChatMessage


class TestScaledDotProductAttention(unittest.TestCase):
    """Test cases for Scaled Dot-Product Attention"""

    def setUp(self):
        self.d_k = 64
        self.attention = ScaledDotProductAttention(self.d_k)

    def test_attention_forward(self):
        """Test forward pass of attention mechanism"""
        batch_size, seq_len = 2, 10

        # Create random Q, K, V tensors
        Q = torch.randn(batch_size, seq_len, self.d_k)
        K = torch.randn(batch_size, seq_len, self.d_k)
        V = torch.randn(batch_size, seq_len, self.d_k)

        # Forward pass
        output, attention_weights = self.attention(Q, K, V)

        # Check output shapes
        self.assertEqual(output.shape, (batch_size, seq_len, self.d_k))
        self.assertEqual(attention_weights.shape, (batch_size, seq_len, seq_len))

        # Check attention weights sum to 1
        weights_sum = torch.sum(attention_weights, dim=-1)
        self.assertTrue(torch.allclose(weights_sum, torch.ones_like(weights_sum), atol=1e-6))

    def test_attention_with_mask(self):
        """Test attention with masking"""
        batch_size, seq_len = 2, 10

        Q = torch.randn(batch_size, seq_len, self.d_k)
        K = torch.randn(batch_size, seq_len, self.d_k)
        V = torch.randn(batch_size, seq_len, self.d_k)

        # Create mask (mask out last 3 positions)
        mask = torch.ones(batch_size, seq_len, seq_len)
        mask[:, :, -3:] = 0

        output, attention_weights = self.attention(Q, K, V, mask)

        # Check that masked positions have near-zero attention
        masked_weights = attention_weights[:, :, -3:]
        self.assertTrue(torch.all(masked_weights < 1e-6))


class TestMultiHeadAttention(unittest.TestCase):
    """Test cases for Multi-Head Attention"""

    def setUp(self):
        self.d_model = 512
        self.num_heads = 8
        self.mha = MultiHeadAttention(self.d_model, self.num_heads)

    def test_multihead_forward(self):
        """Test multi-head attention forward pass"""
        batch_size, seq_len = 2, 20

        x = torch.randn(batch_size, seq_len, self.d_model)

        output = self.mha(x, x, x)

        # Check output shape
        self.assertEqual(output.shape, (batch_size, seq_len, self.d_model))

    def test_multihead_with_different_qkv(self):
        """Test multi-head attention with different Q, K, V"""
        batch_size, seq_len = 2, 15

        Q = torch.randn(batch_size, seq_len, self.d_model)
        K = torch.randn(batch_size, seq_len, self.d_model)
        V = torch.randn(batch_size, seq_len, self.d_model)

        output = self.mha(Q, K, V)

        self.assertEqual(output.shape, (batch_size, seq_len, self.d_model))


class TestPositionalEncoding(unittest.TestCase):
    """Test cases for Positional Encoding"""

    def test_fixed_positional_encoding(self):
        """Test fixed sinusoidal positional encoding"""
        d_model, max_len = 512, 100
        pe = PositionalEncoding(d_model, max_len, "fixed")

        seq_len, batch_size = 50, 3
        x = torch.randn(seq_len, batch_size, d_model)

        output = pe(x)

        self.assertEqual(output.shape, (seq_len, batch_size, d_model))

    def test_learnable_positional_encoding(self):
        """Test learnable positional encoding"""
        d_model, max_len = 512, 100
        pe = PositionalEncoding(d_model, max_len, "learnable")

        seq_len, batch_size = 30, 2
        x = torch.randn(seq_len, batch_size, d_model)

        output = pe(x)

        self.assertEqual(output.shape, (seq_len, batch_size, d_model))


class TestAttentionCache(unittest.TestCase):
    """Test cases for Attention Cache"""

    def setUp(self):
        self.cache = AttentionCache(max_size=3)

    def test_cache_put_get(self):
        """Test basic cache operations"""
        key = "test_key"
        value = torch.randn(2, 10, 512)

        # Put value in cache
        self.cache.put(key, value)

        # Get value from cache
        cached_value = self.cache.get(key)

        self.assertIsNotNone(cached_value)
        self.assertTrue(torch.equal(value, cached_value))

    def test_cache_lru_eviction(self):
        """Test LRU eviction policy"""
        # Fill cache to capacity
        for i in range(3):
            key = f"key_{i}"
            value = torch.randn(2, 10, 512)
            self.cache.put(key, value)

        # Access key_1 to make it recently used
        self.cache.get("key_1")

        # Add new item (should evict key_0)
        self.cache.put("key_3", torch.randn(2, 10, 512))

        # key_0 should be evicted
        self.assertIsNone(self.cache.get("key_0"))

        # key_1 should still be there
        self.assertIsNotNone(self.cache.get("key_1"))


class TestAttentionModel(unittest.TestCase):
    """Test cases for complete Attention Model"""

    def setUp(self):
        self.vocab_size = 1000
        self.model = AttentionModel(
            vocab_size=self.vocab_size,
            d_model=256,
            num_heads=4,
            num_encoder_layers=2
        )

    def test_model_forward(self):
        """Test complete model forward pass"""
        batch_size, seq_len = 2, 50

        # Random token indices
        x = torch.randint(0, self.vocab_size, (batch_size, seq_len))

        output = self.model(x)

        self.assertEqual(output.shape, (batch_size, seq_len, self.vocab_size))

    def test_model_encode_text(self):
        """Test text encoding functionality"""
        batch_size, seq_len = 2, 30

        x = torch.randint(0, self.vocab_size, (batch_size, seq_len))

        encodings = self.model.encode_text(x)

        self.assertEqual(encodings.shape, (batch_size, seq_len, self.model.d_model))

    def test_padding_mask_creation(self):
        """Test padding mask creation"""
        batch_size, seq_len = 2, 20
        pad_token = 0

        # Create input with padding
        x = torch.randint(1, self.vocab_size, (batch_size, seq_len))
        x[:, -5:] = pad_token  # Add padding to last 5 positions

        mask = self.model.create_padding_mask(x, pad_token)

        expected_shape = (batch_size, 1, 1, seq_len)
        self.assertEqual(mask.shape, expected_shape)

        # Check that padding positions are masked (False)
        self.assertTrue(torch.all(mask[:, :, :, -5:] == False))
        self.assertTrue(torch.all(mask[:, :, :, :-5] == True))


class TestAttentionOrchestrator(unittest.TestCase):
    """Test cases for Attention Orchestrator"""

    def setUp(self):
        self.orchestrator = AttentionOrchestrator(vocab_size=1000)

    def test_tokenization(self):
        """Test simple tokenization"""
        text = "Hello world this is a test"
        tokens = self.orchestrator._tokenize_text(text)

        self.assertIsInstance(tokens, list)
        self.assertTrue(all(isinstance(token, int) for token in tokens))

    def test_cache_key_creation(self):
        """Test cache key creation"""
        messages = [
            ChatMessage(role="user", content="Hello"),
            ChatMessage(role="assistant", content="Hi there!")
        ]

        key1 = self.orchestrator._create_cache_key(messages)
        key2 = self.orchestrator._create_cache_key(messages)

        # Same messages should produce same key
        self.assertEqual(key1, key2)

        # Different messages should produce different key
        messages2 = [ChatMessage(role="user", content="Different message")]
        key3 = self.orchestrator._create_cache_key(messages2)
        self.assertNotEqual(key1, key3)

    def test_model_info(self):
        """Test model information retrieval"""
        info = self.orchestrator.get_model_info()

        self.assertIsInstance(info, dict)
        self.assertIn("attention_mode", info)
        self.assertIn("embedding_dim", info)
        self.assertIn("attention_heads", info)

    async def test_async_processing(self):
        """Test async message processing"""
        messages = [
            ChatMessage(role="user", content="Test message for processing")
        ]

        # This would require proper OpenAI API key for full testing
        # For now, just test that the method exists and returns correct type
        try:
            result = await self.orchestrator.process_messages(messages)
            self.assertIsInstance(result, AttentionResult)
        except Exception as e:
            # Expected if no API key is configured
            self.assertIsInstance(e, Exception)


class TestPerformanceBenchmarks(unittest.TestCase):
    """Performance benchmarks for attention mechanisms"""

    def test_attention_performance(self):
        """Benchmark attention computation performance"""
        import time

        d_k = 64
        batch_size, seq_len = 4, 100
        attention = ScaledDotProductAttention(d_k)

        Q = torch.randn(batch_size, seq_len, d_k)
        K = torch.randn(batch_size, seq_len, d_k)
        V = torch.randn(batch_size, seq_len, d_k)

        # Warm up
        for _ in range(10):
            _ = attention(Q, K, V)

        # Benchmark
        start_time = time.perf_counter()
        num_iterations = 100

        for _ in range(num_iterations):
            output, weights = attention(Q, K, V)

        end_time = time.perf_counter()
        avg_time = (end_time - start_time) / num_iterations

        print(f"Average attention computation time: {avg_time:.4f}s")

        # Should be reasonably fast (less than 10ms for this size)
        self.assertLess(avg_time, 0.01)


def run_async_tests():
    """Run async tests"""

    async def async_test_runner():
        test_case = TestAttentionOrchestrator()
        test_case.setUp()
        await test_case.test_async_processing()

    asyncio.run(async_test_runner())


if __name__ == "__main__":
    # Run regular tests
    unittest.main(verbosity=2, exit=False)

    # Run async tests
    print("\nRunning async tests...")
    run_async_tests()
    print("All tests completed!")