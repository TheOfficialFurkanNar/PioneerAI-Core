# 🧠 PioneerAI v1.0 – Adaptive Simulation & Intelligence Framework
PioneerAI is a modular, memory-driven AI framework designed for scalable simulation, secure communication, and ethical orchestration. Initially focused on education fairness, its architecture now supports advanced task routing, adaptive memory, JWT-secured APIs, and asynchronous workflows suitable for research-grade applications.

🚀 Core Capabilities
| Feature | Description | 
| Orchestration Engine | Intent-aware, token-sensitive routing of AI logic | 
| Memory Management | Adaptive context tracking via JSON/Redis + attention decay policies | 
| Authentication | Secure JWT-based login system with salted password hashing | 
| Model Routing | Dynamic selection between GPT‑4o and GPT‑3.5-turbo via token budget | 
| Language Autonomy | Tone shaping, ethical filtering, and semantic HTML surface generation | 
| Simulation Modules | Fairness metrics (Gini, accessibility ratios), system modeling, report generation | 
| Token Intelligence | TokenCounter integration for consumption tracking, throttling, and audit | 
| Async Architecture | Fully asynchronous I/O operations with backpressure resilience | 
| CLI & Frontend Support | Chat-style CLI + React-compatible frontend integration | 



📁 File Structure (Highlights)
📦 src/
 ┣ main.py                 – Entry point (async CLI orchestrator)
 ┣ memory_manager.py       – Adaptive memory storage + Redis readiness
 ┣ token_counter.py        – Token-aware estimation and budgeting
 ┣ auth_routes.py          – JWT endpoints (login, register, verify)
 ┣ chat_client.py          – OpenAI API wrapper with retry/fallback logic
 ┣ orchestrator.py         – Session-state routing and decision policies
 ┣ settings.py             – Global model parameters and attention control
 ┗ fairness_metrics.py     – Equity scoring logic (Gini, access levels)



🧪 Example Session
$ python main.py
🧠 PioneerAI v2.0 initialized – Secure async architecture active!
💬 You: !stats
📊 Session Stats:
• Messages: 36
• Uptime: 21.8 minutes
• Memory: Active



⚙️ ENV Configuration (.env.safe)
OPENAI_MODEL=gpt-4o
SYSTEM_PROMPT="You are PioneerChat, a thoughtful and ethical assistant."
MAX_TOKENS=500
SESSION_TIMEOUT=300
MEMORY_JSON=memory.json
ATTENTION_MODE=hybrid
CACHE_SIZE=1000



🔐 Security Overview
- ✅ Bcrypt password hashing + JWT (24h token expiry)
- ✅ CORS support + Turkish error messages
- ✅ Protected chat endpoints (/ask/summary, /userinfo)
- ✅ Input validation (email, username, token integrity)

📬 Collaboration
This project welcomes feedback, feature requests, and research partnerships.
Maintainer: Furkan
📧 pioneerai.code@gmail.com
📱 +90 541 718 07 66

##  Development Status  
PioneerAI is in active development. While all core modules are functional, model training and full-scale analytics pipelines are evolving. Feedback and contributions are welcome.

##  Requirements  
Python 3.10+  
Libraries: NumPy, Pandas, Matplotlib, Scikit-learn (see `requirements.txt`)

##License
Don't forget to check out the MIT License.


