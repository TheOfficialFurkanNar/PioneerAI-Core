from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict

@dataclass
class UserInteraction:
    user_id: str
    message: str
    timestamp: datetime
    intent: Optional[str] = None
    tone: Optional[str] = None
    tokens: Optional[int] = None
    model_used: Optional[str] = None

    def is_valid(self) -> bool:
        return (
            isinstance(self.user_id, str) and
            bool(self.message.strip()) and
            isinstance(self.timestamp, datetime)
        )

    def to_dict(self) -> Dict:
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