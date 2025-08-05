# examples/attention_demo.py

"""
Demonstration script for PioneerAI's Scaled Dot-Product Attention implementation

This script shows how to use the attention mechanism in different modes:
- Local attention processing
- OpenAI API processing
- Hybrid mode with intelligent routing
"""

import asyncio
import sys
import os
import logging

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.attention_orchestrator import attention_orchestrator
from modules.orchestrator import (
    handle_attention_message, handle_hybrid_message,
    get_attention_info, clear_attention_cache
)
from modules.chat_client import ChatMessage
from config.settings import ATTENTION_MODE

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def demo_basic_attention():
    """Demonstrate basic attention processing"""
    print("🧠 Basic Attention Processing Demo")
    print("=" * 50)

    messages = [
        "Hello, how are you today?",
        "What is the capital of Turkey?",
        "Explain quantum computing in simple terms",
        "Write a short poem about artificial intelligence"
    ]

    for i, message in enumerate(messages, 1):
        print(f"\n📝 Message {i}: {message}")

        try:
            result = await handle_attention_message("demo_user", message)

            print(f"🤖 Response: {result['reply']}")
            print(f"📊 Method: {result['meta'].get('method', 'unknown')}")
            print(f"⚡ Confidence: {result['meta'].get('confidence', 0):.2f}")
            print(f"⏱️  Latency: {result['meta'].get('latency', 0):.2f}s")

        except Exception as e:
            print(f"❌ Error: {e}")

        print("-" * 30)


async def demo_hybrid_processing():
    """Demonstrate hybrid attention + summarization"""
    print("\n🔥 Hybrid Processing Demo")
    print("=" * 50)

    messages = [
        "Can you summarize the benefits of renewable energy?",
        "What are the main challenges in machine learning?",
        "Explain the concept of blockchain technology"
    ]

    for i, message in enumerate(messages, 1):
        print(f"\n📝 Message {i}: {message}")

        try:
            result = await handle_hybrid_message("demo_user", message)

            print(f"🤖 Response: {result['reply']}")
            print(f"📊 Method: {result['meta'].get('method', 'unknown')}")

            if 'confidence' in result['meta']:
                print(f"⚡ Confidence: {result['meta']['confidence']:.2f}")
            if 'attention_confidence' in result['meta']:
                print(f"🧠 Attention Confidence: {result['meta']['attention_confidence']:.2f}")

            print(f"⏱️  Latency: {result['meta'].get('latency', 0):.2f}s")

        except Exception as e:
            print(f"❌ Error: {e}")

        print("-" * 30)


async def demo_streaming_attention():
    """Demonstrate streaming attention responses"""
    print("\n🌊 Streaming Attention Demo")
    print("=" * 50)

    message = "Tell me about the future of artificial intelligence"
    print(f"📝 Message: {message}")
    print("🤖 Streaming Response: ", end="", flush=True)

    try:
        from modules.orchestrator import handle_stream_attention_message

        async for chunk in handle_stream_attention_message("demo_user", message):
            print(chunk, end="", flush=True)

        print("\n✅ Streaming completed")

    except Exception as e:
        print(f"\n❌ Streaming Error: {e}")


def demo_attention_cache():
    """Demonstrate attention caching"""
    print("\n💾 Attention Cache Demo")
    print("=" * 50)

    # Show cache info
    info = get_attention_info()
    print(f"Cache Enabled: {info.get('cache_enabled', False)}")

    if info.get('cache_enabled'):
        print("🧹 Clearing cache...")
        clear_attention_cache()
        print("✅ Cache cleared")
    else:
        print("ℹ️  Cache is disabled")


async def demo_direct_orchestrator():
    """Demonstrate direct orchestrator usage"""
    print("\n🎯 Direct Orchestrator Demo")
    print("=" * 50)

    messages = [
        ChatMessage(role="user", content="What is machine learning?"),
        ChatMessage(role="assistant", content="Machine learning is a subset of AI..."),
        ChatMessage(role="user", content="Can you give me an example?")
    ]

    try:
        result = await attention_orchestrator.process_messages(messages)

        print(f"🤖 Response: {result.content}")
        print(f"📊 Method: {result.method}")
        print(f"⚡ Confidence: {result.confidence:.2f}")
        print(f"⏱️  Processing Time: {result.processing_time:.2f}s")

    except Exception as e:
        print(f"❌ Error: {e}")


def show_system_info():
    """Show attention system information"""
    print("🔧 PioneerAI Attention System Information")
    print("=" * 50)

    info = get_attention_info()

    print(f"Attention Mode: {info.get('attention_mode', 'unknown')}")
    print(f"Embedding Dimension: {info.get('embedding_dim', 'unknown')}")
    print(f"Attention Heads: {info.get('attention_heads', 'unknown')}")
    print(f"Sequence Length: {info.get('sequence_length', 'unknown')}")
    print(f"Cache Enabled: {info.get('cache_enabled', False)}")
    print(f"Local Model Loaded: {info.get('local_model_loaded', False)}")

    if 'model_parameters' in info:
        params = info['model_parameters']
        print(f"Model Parameters: {params:,}")
        print(f"Model Size: ~{params * 4 / 1024 / 1024:.1f} MB (float32)")


async def interactive_demo():
    """Interactive demo for testing attention"""
    print("\n💬 Interactive Attention Demo")
    print("=" * 50)
    print("Type your messages (type 'quit' to exit):")

    while True:
        try:
            message = input("\n👤 You: ").strip()

            if message.lower() in ['quit', 'exit', 'q']:
                break

            if not message:
                continue

            print("🤖 PioneerAI: ", end="", flush=True)

            # Use streaming for interactive feel
            from modules.orchestrator import handle_stream_attention_message

            async for chunk in handle_stream_attention_message("interactive_user", message):
                print(chunk, end="", flush=True)

            print()  # New line after response

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

    print("\n👋 Goodbye!")


async def main():
    """Main demo function"""
    print("🚀 PioneerAI Scaled Dot-Product Attention Demo")
    print("=" * 60)

    # Show system information
    show_system_info()

    # Run demos based on user choice
    print("\nAvailable demos:")
    print("1. Basic Attention Processing")
    print("2. Hybrid Processing")
    print("3. Streaming Attention")
    print("4. Cache Demo")
    print("5. Direct Orchestrator")
    print("6. Interactive Demo")
    print("7. Run All Demos")

    try:
        choice = input("\nSelect demo (1-7): ").strip()

        if choice == "1":
            await demo_basic_attention()
        elif choice == "2":
            await demo_hybrid_processing()
        elif choice == "3":
            await demo_streaming_attention()
        elif choice == "4":
            demo_attention_cache()
        elif choice == "5":
            await demo_direct_orchestrator()
        elif choice == "6":
            await interactive_demo()
        elif choice == "7":
            await demo_basic_attention()
            await demo_hybrid_processing()
            await demo_streaming_attention()
            demo_attention_cache()
            await demo_direct_orchestrator()
        else:
            print("Invalid choice. Running basic demo...")
            await demo_basic_attention()

    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")

    print("\n✅ Demo completed!")


if __name__ == "__main__":
    # Set up environment for demo
    os.environ.setdefault("ATTENTION_MODE", "hybrid")
    os.environ.setdefault("ATTENTION_CACHE_ENABLED", "True")

    # Run the demo
    asyncio.run(main())