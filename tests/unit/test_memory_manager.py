import asyncio
from modules.memory_manager import set_user_conversation, get_user_conversation

async def test_memory_manager():
    user_id = "furkan"
    conv = [{"msg": "Hello"}, {"msg": "World"}]

    # Konuşmayı hem diske hem cache’e kaydet
    await set_user_conversation(user_id, conv)

    # Kaydedileni geri oku
    cached = await get_user_conversation(user_id)

    # Beklenen ve geriye dönen değer eşit olmalı
    assert cached == conv, f"Beklenen {conv}, dönen {cached}"

    print("✅ test_memory_manager geçti:", cached)

if __name__ == "__main__":
    asyncio.run(test_memory_manager())