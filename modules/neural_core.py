# modules/neural_core.py

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Dict, Any
import logging
import os

from config.settings import (
    EMBEDDING_DIM, SEQUENCE_LENGTH, DROPOUT_RATE,
    NUM_ENCODER_LAYERS, NUM_DECODER_LAYERS,
    PRE_TRAINED_EMBEDDINGS, POSITIONAL_ENCODING_TYPE
)
from .attention_layer import MultiHeadAttention, PositionalEncoding


class TokenEmbedding(nn.Module):
    """
    Token embedding layer with optional pre-trained embeddings
    """

    def __init__(
            self,
            vocab_size: int,
            d_model: int = EMBEDDING_DIM,
            pretrained_path: str = PRE_TRAINED_EMBEDDINGS
    ):
        super(TokenEmbedding, self).__init__()

        self.d_model = d_model
        self.embedding = nn.Embedding(vocab_size, d_model)

        # Load pre-trained embeddings if available
        if pretrained_path and os.path.exists(pretrained_path):
            self._load_pretrained_embeddings(pretrained_path)
        else:
            # Initialize with Xavier uniform
            nn.init.xavier_uniform_(self.embedding.weight)

        self.logger = logging.getLogger(__name__)

    def _load_pretrained_embeddings(self, path: str):
        """Load pre-trained embeddings from file"""
        try:
            embeddings = torch.load(path)
            self.embedding.weight.data.copy_(embeddings)
            self.logger.info(f"Loaded pre-trained embeddings from {path}")
        except Exception as e:
            self.logger.warning(f"Failed to load pre-trained embeddings: {e}")
            nn.init.xavier_uniform_(self.embedding.weight)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass for token embedding

        Args:
            x: Token indices [batch_size, seq_len]

        Returns:
            embeddings: Token embeddings [batch_size, seq_len, d_model]
        """
        return self.embedding(x) * math.sqrt(self.d_model)


class FeedForward(nn.Module):
    """
    Position-wise feed-forward network
    """

    def __init__(
            self,
            d_model: int = EMBEDDING_DIM,
            d_ff: int = None,
            dropout: float = DROPOUT_RATE
    ):
        super(FeedForward, self).__init__()

        if d_ff is None:
            d_ff = d_model * 4  # Standard transformer ratio

        self.linear1 = nn.Linear(d_model, d_ff)
        self.linear2 = nn.Linear(d_ff, d_model)
        self.dropout = nn.Dropout(dropout)
        self.layer_norm = nn.LayerNorm(d_model)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass for feed-forward network

        Args:
            x: Input tensor [batch_size, seq_len, d_model]

        Returns:
            output: Feed-forward output [batch_size, seq_len, d_model]
        """
        residual = x

        x = self.linear1(x)
        x = F.relu(x)
        x = self.dropout(x)
        x = self.linear2(x)
        x = self.dropout(x)

        # Residual connection and layer normalization
        return self.layer_norm(x + residual)


class TransformerEncoderLayer(nn.Module):
    """
    Single transformer encoder layer
    """

    def __init__(
            self,
            d_model: int = EMBEDDING_DIM,
            num_heads: int = 8,
            d_ff: int = None,
            dropout: float = DROPOUT_RATE
    ):
        super(TransformerEncoderLayer, self).__init__()

        self.self_attention = MultiHeadAttention(d_model, num_heads, dropout)
        self.feed_forward = FeedForward(d_model, d_ff, dropout)

    def forward(
            self,
            x: torch.Tensor,
            mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Forward pass for encoder layer

        Args:
            x: Input tensor [batch_size, seq_len, d_model]
            mask: Optional attention mask

        Returns:
            output: Encoder layer output [batch_size, seq_len, d_model]
        """
        # Self-attention
        x = self.self_attention(x, x, x, mask)

        # Feed-forward
        x = self.feed_forward(x)

        return x


class TransformerEncoder(nn.Module):
    """
    Multi-layer transformer encoder
    """

    def __init__(
            self,
            num_layers: int = NUM_ENCODER_LAYERS,
            d_model: int = EMBEDDING_DIM,
            num_heads: int = 8,
            d_ff: int = None,
            dropout: float = DROPOUT_RATE
    ):
        super(TransformerEncoder, self).__init__()

        self.layers = nn.ModuleList([
            TransformerEncoderLayer(d_model, num_heads, d_ff, dropout)
            for _ in range(num_layers)
        ])

        self.layer_norm = nn.LayerNorm(d_model)

    def forward(
            self,
            x: torch.Tensor,
            mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Forward pass for transformer encoder

        Args:
            x: Input tensor [batch_size, seq_len, d_model]
            mask: Optional attention mask

        Returns:
            output: Encoder output [batch_size, seq_len, d_model]
        """
        for layer in self.layers:
            x = layer(x, mask)

        return self.layer_norm(x)


class AttentionModel(nn.Module):
    """
    Complete attention-based model for text processing
    """

    def __init__(
            self,
            vocab_size: int,
            d_model: int = EMBEDDING_DIM,
            num_heads: int = 8,
            num_encoder_layers: int = NUM_ENCODER_LAYERS,
            max_seq_len: int = SEQUENCE_LENGTH,
            dropout: float = DROPOUT_RATE,
            positional_encoding_type: str = POSITIONAL_ENCODING_TYPE
    ):
        super(AttentionModel, self).__init__()

        self.d_model = d_model
        self.vocab_size = vocab_size

        # Core components
        self.token_embedding = TokenEmbedding(vocab_size, d_model)
        self.positional_encoding = PositionalEncoding(
            d_model, max_seq_len, positional_encoding_type
        )
        self.encoder = TransformerEncoder(
            num_encoder_layers, d_model, num_heads, dropout=dropout
        )

        # Output projection
        self.output_projection = nn.Linear(d_model, vocab_size)

        self.dropout = nn.Dropout(dropout)
        self.logger = logging.getLogger(__name__)

    def create_padding_mask(self, x: torch.Tensor, pad_token: int = 0) -> torch.Tensor:
        """
        Create padding mask for attention

        Args:
            x: Input token indices [batch_size, seq_len]
            pad_token: Padding token index

        Returns:
            mask: Padding mask [batch_size, 1, 1, seq_len]
        """
        mask = (x != pad_token).unsqueeze(1).unsqueeze(2)
        return mask

    def forward(
            self,
            x: torch.Tensor,
            mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Forward pass for attention model

        Args:
            x: Input token indices [batch_size, seq_len]
            mask: Optional attention mask

        Returns:
            output: Model output [batch_size, seq_len, vocab_size]
        """
        # Create padding mask if not provided
        if mask is None:
            mask = self.create_padding_mask(x)

        # Token embedding
        x = self.token_embedding(x)

        # Positional encoding
        x = x.transpose(0, 1)  # [seq_len, batch_size, d_model]
        x = self.positional_encoding(x)
        x = x.transpose(0, 1)  # [batch_size, seq_len, d_model]

        x = self.dropout(x)

        # Encoder
        x = self.encoder(x, mask)

        # Output projection
        output = self.output_projection(x)

        return output

    def encode_text(
            self,
            x: torch.Tensor,
            mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Encode text to contextual representations

        Args:
            x: Input token indices [batch_size, seq_len]
            mask: Optional attention mask

        Returns:
            encodings: Contextual encodings [batch_size, seq_len, d_model]
        """
        if mask is None:
            mask = self.create_padding_mask(x)

        # Token embedding
        x = self.token_embedding(x)

        # Positional encoding
        x = x.transpose(0, 1)
        x = self.positional_encoding(x)
        x = x.transpose(0, 1)

        x = self.dropout(x)

        # Encoder
        encodings = self.encoder(x, mask)

        return encodings

    def get_attention_weights(
            self,
            x: torch.Tensor,
            layer_idx: int = -1
    ) -> torch.Tensor:
        """
        Extract attention weights from a specific layer

        Args:
            x: Input token indices [batch_size, seq_len]
            layer_idx: Layer index to extract weights from (-1 for last layer)

        Returns:
            attention_weights: Attention weights [batch_size, num_heads, seq_len, seq_len]
        """
        # This would require modifying the forward pass to return attention weights
        # For now, return None as placeholder
        self.logger.warning("Attention weight extraction not implemented yet")
        return None


import math  # Add missing import