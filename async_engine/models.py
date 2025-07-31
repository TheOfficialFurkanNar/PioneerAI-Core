from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict

@dataclass
class UserInteraction:
    """
    Represents a user's interaction with the AI, including metadata.
    """
    user_id: str
    message: str
    timestamp: datetime
    intent: Optional[str] = None
    tone: Optional[str] = None
    tokens: Optional[int] = None
    model_used: Optional[str] = None

    def is_valid(self) -> bool:
        """Check essential fields for validity."""
        return (
            isinstance(self.user_id, str) and
            bool(self.message.strip()) and
            isinstance(self.timestamp, datetime)
        )

    def to_dict(self) -> Dict:
        """Serialize the object to a dictionary."""
        return {
            "user_id": self.user_id,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "intent": self.intent,
            "tone": self.tone,
            "tokens": self.tokens,
            "model_used": self.model_used
        }

    @staticmethod
    def from_dict(data: Dict) -> "UserInteraction":
        """Deserialize a dictionary to a UserInteraction instance."""
        try:
            return UserInteraction(
                user_id=data.get("user_id", ""),
                message=data.get("message", ""),
                timestamp=datetime.fromisoformat(data.get("timestamp")),
                intent=data.get("intent"),
                tone=data.get("tone"),
                tokens=data.get("tokens"),
                model_used=data.get("model_used")
            )
        except Exception as e:
            raise ValueError(f"[Parse Error] Veri modeli oluşturulamadı: {e}")