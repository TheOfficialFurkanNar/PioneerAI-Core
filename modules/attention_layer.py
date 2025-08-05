# modules/attention_layer.py

import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple
import logging

from config.settings import (
<< << << < HEAD
ATTENTION_HEADS, EMBEDDING_DIM, DROPOUT_RATE,
== == == =
ATTENTION_HEADS, EMBEDDING_DIM, DROPOUT_RATE,
>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165
SEQUENCE_LENGTH, ATTENTION_CACHE_ENABLED
)

class ScaledDotProductAttention(nn.Module):
    """
    Scaled Dot-Product Attention implementation
<<<<<<< HEAD

    Attention(Q,K,V) = softmax(QK^T/√d_k)V
    """

== == == =

Attention(Q, K, V) = softmax(QK ^ T /√d_k)V
"""

>>>>>>> 0285be0883ab9d10884b57d1097c61f567b39165
def __init__(self, d_k: int, dropout: float = 0.1):
    super(ScaledDotProductAttention, self).__init__()
    self.d_k = d_k
    self.dropout = nn.Dropout(dropout)
    self.logger = logging.getLogger(__name__)
<<<<<<< HEAD

def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        mask: Optional[torch.Tensor] = None
) -> Tuple[torch.Tensor, torch.Tensor]:
    """
Forward
pass
for scaled dot - product attention

== == == =

def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        mask: Optional[torch.Tensor] = None
) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    Forward pass for scaled dot-product attention

>>>>>>> 0285be0883ab9d10884b57d1097c61f567b39165
    Args:
        query: Query tensor [batch_size, seq_len, d_k]
        key: Key tensor [batch_size, seq_len, d_k]
        value: Value tensor [batch_size, seq_len, d_v]
        mask: Optional attention mask [batch_size, seq_len, seq_len]
<<<<<<< HEAD

=======

>>>>>>> 0285be0883ab9d10884b57d1097c61f567b39165
    Returns:
        output: Attention output [batch_size, seq_len, d_v]
        attention_weights: Attention weights [batch_size, seq_len, seq_len]
    """
    batch_size, seq_len, d_k = query.size()

<< << << < HEAD

# Calculate attention scores: QK^T / √d_k
scores = torch.matmul(query, key.transpose(-2, -1)) / math.sqrt(self.d_k)

# Apply mask if provided (for padding or causal attention)
if mask is not None:
    scores = scores.masked_fill(mask == 0, -1e9)

# Apply softmax to get attention weights
attention_weights = F.softmax(scores, dim=-1)
attention_weights = self.dropout(attention_weights)

# Apply attention weights to values
output = torch.matmul(attention_weights, value)

== == == =

# Calculate attention scores: QK^T / √d_k
scores = torch.matmul(query, key.transpose(-2, -1)) / math.sqrt(self.d_k)

# Apply mask if provided (for padding or causal attention)
if mask is not None:
    scores = scores.masked_fill(mask == 0, -1e9)

# Apply softmax to get attention weights
attention_weights = F.softmax(scores, dim=-1)
attention_weights = self.dropout(attention_weights)

# Apply attention weights to values
output = torch.matmul(attention_weights, value)

>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165
return output, attention_weights


class MultiHeadAttention(nn.Module):
    """
    Multi-Head Attention mechanism
<<<<<<< HEAD

    Combines multiple attention heads for richer representation learning
    """

    def __init__(
            self,
            d_model: int = EMBEDDING_DIM,
            num_heads: int = ATTENTION_HEADS,
            dropout: float = DROPOUT_RATE
    ):
        super(MultiHeadAttention, self).__init__()

        assert d_model % num_heads == 0, "d_model must be divisible by num_heads"

        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads

== == == =

Combines
multiple
attention
heads
for richer representation learning
"""

def __init__(
    self, 
    d_model: int = EMBEDDING_DIM, 
    num_heads: int = ATTENTION_HEADS, 
    dropout: float = DROPOUT_RATE
):
    super(MultiHeadAttention, self).__init__()

    assert d_model % num_heads == 0, "d_model must be divisible by num_heads"

    self.d_model = d_model
    self.num_heads = num_heads
    self.d_k = d_model // num_heads

>>>>>>> 0285be0883ab9d10884b57d1097c61f567b39165
    # Linear projections for Q, K, V
    self.w_q = nn.Linear(d_model, d_model)
    self.w_k = nn.Linear(d_model, d_model)
    self.w_v = nn.Linear(d_model, d_model)
    self.w_o = nn.Linear(d_model, d_model)
<<<<<<< HEAD

=======

>>>>>>> 0285be0883ab9d10884b57d1097c61f567b39165
    # Attention mechanism
    self.attention = ScaledDotProductAttention(self.d_k, dropout)
    self.dropout = nn.Dropout(dropout)
    self.layer_norm = nn.LayerNorm(d_model)
<<<<<<< HEAD

    self.logger = logging.getLogger(__name__)

def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        mask: Optional[torch.Tensor] = None
) -> torch.Tensor:
    """
Forward
pass
for multi - head attention

== == == =

self.logger = logging.getLogger(__name__)


def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        mask: Optional[torch.Tensor] = None
) -> torch.Tensor:
    """
    Forward pass for multi-head attention

>>>>>>> 0285be0883ab9d10884b57d1097c61f567b39165
    Args:
        query: Query tensor [batch_size, seq_len, d_model]
        key: Key tensor [batch_size, seq_len, d_model]
        value: Value tensor [batch_size, seq_len, d_model]
        mask: Optional attention mask
<<<<<<< HEAD

=======

>>>>>>> 0285be0883ab9d10884b57d1097c61f567b39165
    Returns:
        output: Multi-head attention output [batch_size, seq_len, d_model]
    """
    batch_size, seq_len, d_model = query.size()
    residual = query

<< << << < HEAD

== == == =

>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165
# 1. Linear projections in batch from d_model => h x d_k
Q = self.w_q(query).view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
K = self.w_k(key).view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
V = self.w_v(value).view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
<< << << < HEAD

# 2. Apply attention on all the projected vectors in batch
if mask is not None:
    mask = mask.unsqueeze(1).repeat(1, self.num_heads, 1, 1)

attn_output, attention_weights = self.attention(Q, K, V, mask)

== == == =

# 2. Apply attention on all the projected vectors in batch
if mask is not None:
    mask = mask.unsqueeze(1).repeat(1, self.num_heads, 1, 1)

attn_output, attention_weights = self.attention(Q, K, V, mask)

>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165
# 3. Concatenate heads and put through final linear layer
attn_output = attn_output.transpose(1, 2).contiguous().view(
    batch_size, seq_len, self.d_model
)
<< << << < HEAD

output = self.w_o(attn_output)
output = self.dropout(output)

# 4. Add residual connection and layer normalization
output = self.layer_norm(output + residual)

== == == =

output = self.w_o(attn_output)
output = self.dropout(output)

# 4. Add residual connection and layer normalization
output = self.layer_norm(output + residual)

>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165
return output


class PositionalEncoding(nn.Module):
    """
    Positional encoding for transformer models
<<<<<<< HEAD

    Supports both fixed sinusoidal and learnable positional encodings
    """

    def __init__(
            self,
            d_model: int = EMBEDDING_DIM,
            max_len: int = SEQUENCE_LENGTH,
            encoding_type: str = "fixed"
    ):
        super(PositionalEncoding, self).__init__()

        self.d_model = d_model
        self.encoding_type = encoding_type

== == == =

Supports
both
fixed
sinusoidal and learnable
positional
encodings
"""

def __init__(
    self, 
    d_model: int = EMBEDDING_DIM, 
    max_len: int = SEQUENCE_LENGTH,
    encoding_type: str = "fixed"
):
    super(PositionalEncoding, self).__init__()

    self.d_model = d_model
    self.encoding_type = encoding_type

>>>>>>> 0285be0883ab9d10884b57d1097c61f567b39165
    if encoding_type == "fixed":
        # Create fixed sinusoidal positional encodings
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
<<<<<<< HEAD

        div_term = torch.exp(torch.arange(0, d_model, 2).float() *
                             (-math.log(10000.0) / d_model))

        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1)

        self.register_buffer('pe', pe)

    elif encoding_type == "learnable":
        # Create learnable positional embeddings
        self.pe = nn.Parameter(torch.randn(max_len, d_model))

    self.dropout = nn.Dropout(DROPOUT_RATE)

def forward(self, x: torch.Tensor) -> torch.Tensor:
    """
Add
positional
encoding
to
input
embeddings

Args:
x: Input
embeddings[seq_len, batch_size, d_model]

== == == =

div_term = torch.exp(torch.arange(0, d_model, 2).float() *
                     (-math.log(10000.0) / d_model))

pe[:, 0::2] = torch.sin(position * div_term)
pe[:, 1::2] = torch.cos(position * div_term)
pe = pe.unsqueeze(0).transpose(0, 1)

self.register_buffer('pe', pe)

elif encoding_type == "learnable":
# Create learnable positional embeddings
self.pe = nn.Parameter(torch.randn(max_len, d_model))

self.dropout = nn.Dropout(DROPOUT_RATE)


def forward(self, x: torch.Tensor) -> torch.Tensor:
    """
    Add positional encoding to input embeddings

    Args:
        x: Input embeddings [seq_len, batch_size, d_model]

>>>>>>> 0285be0883ab9d10884b57d1097c61f567b39165
    Returns:
        x: Embeddings with positional encoding added
    """
    if self.encoding_type == "fixed":
        x = x + self.pe[:x.size(0), :]
    elif self.encoding_type == "learnable":
        x = x + self.pe[:x.size(0), :].unsqueeze(1)

<< << << < HEAD

== == == =

>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165
return self.dropout(x)


class AttentionCache:
    """
    Cache for attention computations to improve performance
    """

<< << << < HEAD

== == == =

>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165


def __init__(self, max_size: int = 1000):
    self.cache = {}
    self.max_size = max_size
    self.access_count = {}
    self.logger = logging.getLogger(__name__)

<< << << < HEAD

== == == =

>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165


def get(self, key: str) -> Optional[torch.Tensor]:
    """Get cached attention result"""
    if key in self.cache:
        self.access_count[key] = self.access_count.get(key, 0) + 1
        return self.cache[key]
    return None

<< << << < HEAD

== == == =

>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165


def put(self, key: str, value: torch.Tensor):
    """Cache attention result with LRU eviction"""
    if len(self.cache) >= self.max_size:
        # Remove least recently used item
        lru_key = min(self.access_count.keys(), key=self.access_count.get)
        del self.cache[lru_key]
        del self.access_count[lru_key]

<< << << < HEAD

self.cache[key] = value.clone().detach()
self.access_count[key] = 1

== == == =

self.cache[key] = value.clone().detach()
self.access_count[key] = 1

>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165


def clear(self):
    """Clear the cache"""
    self.cache.clear()
    self.access_count.clear()
    self.logger.info("Attention cache cleared")


# Global attention cache instance
attention_cache = AttentionCache() if ATTENTION_CACHE_ENABLED else None