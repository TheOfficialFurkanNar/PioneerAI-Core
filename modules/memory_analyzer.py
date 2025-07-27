# modules/memory_analyzer.py

import re
import json
import logging
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, Callable, Optional, Any, Union

class MemoryAnalyzer:
    """
    Kullanıcı konuşmalarından anahtar kelime, tonlama, intent,
    zaman aktivitesi ve GPT destekli özet çıkaran esnek analiz sınıfı.
    """

    def __init__(
        self,
        memory_path: str,
        intent_fn: Optional[Callable[[str], str]] = None,
        summary_fn: Optional[Callable[[str], str]] = None
    ) -> None:
        self.memory_path      = memory_path
        self.intent_fn        = intent_fn
        self.summary_fn       = summary_fn

        self.conversations    : list[Dict[str, Any]] = []
        self.keywords         = Counter()
        self.intent_stats     = Counter()
        self.tone_stats       = {"positive": 0, "negative": 0, "neutral": 0}
        self.activity_by_hour = defaultdict(int)
        self.errors           : list[str] = []
        self.intent_examples  = defaultdict(list)

    # ------------------ Yükleme ------------------
    def load_memory(self) -> None:
        try:
            with open(self.memory_path, encoding="utf-8") as f:
                data = json.load(f)

            # Kök JSON doğrudan liste ise, onu kullanalım
            if isinstance(data, list):
                self.conversations = data
            else:
                # 'conversation' anahtarı altındaki listeyi al
                self.conversations = data.get("conversation", [])
        except Exception as e:
            msg = f"[MEMORY] Yüklenemedi: {e}"
            logging.warning(msg)
            self.errors.append(msg)

    # ------------------ Analizler ------------------
    def extract_keywords(self, min_len: int = 4) -> None:
        for t in self.conversations:
            text = t.get("user", "").lower()
            words = re.findall(r"\b\w+\b", text)
            filtered = [w for w in words if len(w) >= min_len]
            self.keywords.update(filtered)

    def analyze_tone(self) -> None:
        pos = {"teşekkür", "güzel", "başardım", "mutluyum", "etkileyici"}
        neg = {"sorun", "çalışmıyor", "üzücü", "kayıp", "hata"}

        for t in self.conversations:
            text = t.get("user", "").lower()
            if any(w in text for w in pos):
                self.tone_stats["positive"] += 1
            elif any(w in text for w in neg):
                self.tone_stats["negative"] += 1
            else:
                self.tone_stats["neutral"] += 1

    def analyze_intents(self) -> None:
        if not self.intent_fn:
            return

        for t in self.conversations:
            user_text = t.get("user", "")
            intent = self.intent_fn(user_text)
            self.intent_stats[intent] += 1
            if len(self.intent_examples[intent]) < 5:
                self.intent_examples[intent].append(user_text)

    def analyze_activity(self) -> None:
        for t in self.conversations:
            try:
                ts = datetime.fromisoformat(t["timestamp"])
                self.activity_by_hour[ts.hour] += 1
            except Exception:
                continue

    # ------------------ GPT Özetleme ------------------
    def generate_summary(self, turns: int = 8, level: str = "brief") -> str:
        if not self.summary_fn:
            return "🧠 GPT özetleyici bağlı değil."

        convo = self.conversations[-turns:]
        text  = "\n".join(f"You: {t['user']}\nBot : {t.get('bot','')}" for t in convo)
        prompt = f"Aşağıdaki diyaloğu {level} ve anlamlı şekilde özetle:\n{text}"
        return self.summary_fn(prompt)

    # ------------------ Raporlama ------------------
    def report(self) -> Dict[str, Any]:
        return {
            "top_keywords"      : self.keywords.most_common(12),
            "tone_distribution" : self.tone_stats,
            "intent_stats"      : dict(self.intent_stats),
            "activity_by_hour"  : dict(self.activity_by_hour),
            "intent_examples"   : dict(self.intent_examples),
            "errors"            : self.errors
        }

    # ------------------ Otomatik Çağrı ------------------
    def __call__(
        self,
        *,
        analyze_tone: bool = True,
        analyze_intent: bool = True,
        analyze_activity: bool = True
    ) -> Dict[str, Any]:
        self.load_memory()
        self.extract_keywords()
        if analyze_tone:
            self.analyze_tone()
        if analyze_intent:
            self.analyze_intents()
        if analyze_activity:
            self.analyze_activity()
        return {
            "summary": self.generate_summary(),
            "report" : self.report()
        }


# ------------------ CLI Test ------------------
if __name__ == "__main__":
    import logging
    from config.settings import MEMORY_JSON
    from modules.task_router import classify_intent
    from modules.summarizer_agent import SummarizerAgent

    logging.basicConfig(level=logging.INFO)

    # SummarizerAgent'i özetleme fonksiyonu olarak veriyoruz
    agent = SummarizerAgent(memory_path=MEMORY_JSON)
    analyzer = MemoryAnalyzer(
        memory_path=MEMORY_JSON,
        intent_fn=classify_intent,
        summary_fn=lambda prompt: agent.generate_summary("test_user", prompt)
    )

    result = analyzer()

    print("📊 Rapor:")
    print(json.dumps(result["report"], indent=2, ensure_ascii=False))
    print("\n🧠 GPT Özet:")
    print(result["summary"])