# utils/token_counter.py

"""
Basitçe bir metindeki token sayısını ölçer.
Varsa tiktoken kullanır, yoksa boşluk bazlı bir tahmin yapar.
"""

from typing import Optional

try:
    import tiktoken
except ImportError:
    tiktoken = None


def count_tokens(text: str, model: Optional[str] = "gpt-3.5-turbo") -> int:
    """
    Verilen metindeki token sayısını döner.

    1. Eğer tiktoken kurulmuşsa, modelin encoder'ını kullanır.
    2. Aksi halde boşluk bölerek bir tahmin yapar.
    """
    if tiktoken:
        try:
            # Modele göre uygun encoding'i al
            encoder = tiktoken.encoding_for_model(model)
        except KeyError:
            # Modeli tanımadıysa default encoding kullan
            encoder = tiktoken.get_encoding("cl100k_base")
        # Metni encode et ve token listesinin uzunluğunu döndür
        return len(encoder.encode(text))
    else:
        # Basit fallback: boşluklara göre kelime sayısı ≈ token sayısı
        return len(text.split())