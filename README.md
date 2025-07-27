# PioneerAI 1.0   
Fairness-aware simulation framework for analyzing education systems using adaptive AI logic.

##  Overview  
PioneerAI is a modular AI engine designed to simulate educational environments based on fairness metrics.  
It evaluates systemic inequalities and routes simulation tasks using data-driven mechanisms.

##  Key Modules  
- `task_router.py`: Assigns simulation logic based on fairness constraints  
- `settings.py`: Manages global parameters and runtime configurations  
- `simulator_core.py`: Core simulation engine for modeling educational inequalities  
- `ai_engine.py`: Adaptive scoring and decision logic module  
- `fairness_metrics.py`: Calculates equity ratios (Gini, access levels, etc.)  
- `report_generator.py`: Generates visual and text-based simulation reports

##  Development Status  
PioneerAI is in active development. While all core modules are functional, model training and full-scale analytics pipelines are evolving. Feedback and contributions are welcome.

##  Requirements  
Python 3.10+  
Libraries: NumPy, Pandas, Matplotlib, Scikit-learn (see `requirements.txt`)

##  License  
MIT License. See the [LICENSE](./LICENSE) file for details.

##  Contact & Contributions  
Feel free to suggest improvements via Issues or submit PRs.  
Developed by Furkan | Connect via: pioneerai.code@gmail.com |  +90 541 718 07 66
# System Architecture
PioneerAI/
├── main.py                     ← GPT call handler and core intelligence module
├── app.py                      ← Advanced FastAPI server (sync + async capable)
│
├── pioneerchat/                ← AI engine and context management layer
│   ├── __init__.py
│   ├── orchestrator.py         ← Task dispatching and intent classification
│   ├── async_bridge.py         ← Streaming GPT connector
│   ├── conversation_engine.py  ← Dialogue flow controller + context organization
│   ├── memory_manager.py       ← Read/write memory ops (json/txt/db support)
│   ├── memory_analyzer.py      ← Memory analysis + tone, intent + GPT summarization ✅
│   ├── get_context.py          ← Generates context inputs from memory for GPT 🆕
│   ├── agent_router.py         ← intent → custom module routing logic 🆕
│   ├── daily_summary.py        ← Daily conversation summarizer & archiver 🆕
│   └── task_router.py          ← Task classification via intent
│
├── config/
│   ├── settings.py             ← Environment configuration (.env support)
│   ├── .env                    ← API keys, model setup parameters
│   ├── constants.py            ← Versioning, limits, global constants
│   └── colors.py               ← Log coloring helper (optional)
│
├── web/                        ← Web-based user interface
│   ├── index.html              ← Main landing page
│   ├── app.js                  ← JS-based chat event handler
│   ├── style.css               ← Stylesheet
│   ├── memory.js               ← localStorage-based memory tracker
│   ├── intent.js               ← Conditional intent visualizer (optional)
│   └── dashboard.html          ← Memory analyzer + GPT summary dashboard 🆕
│
├── api/                        ← REST API layer
│   ├── __init__.py
│   ├── v1/
│   │   └── routes.py           ← /ask, /analyze, /context-info, /health endpoints 🆕
│   └── utils.py                ← Token counter, JSON helper, error handler 🆕
│
├── memory/
│   ├── memory.json             ← Persistent conversational memory
│   ├── conversation_memory.txt ← Text transcript of interactions
│   ├── summary_YYYYMMDD.json   ← Daily summary records 🆕
│   └── user_context_cache.json ← Cached output from get_context() 🆕
│
├── logs/
│   ├── pioneer.log             ← General conversational logs
│   ├── performance.log         ← Response timing, token metrics
│   ├── error.log               ← Exceptions and error tracking
│   └── summary.log             ← Daily GPT summarization tracking 🆕
│
├── tests/
│   ├── env_check.py
│   ├── version_check.py
│   ├── api_test.py             ← Endpoint tests for /ask and /analyze
│   └── memory_test.py          ← Tests for memoryAnalyzer and context generator 🆕
│
├── static/                     ← Visual assets and uploads
│   └── assets/
│       ├── logo.png
│       └── background.jpg
│
├── requirements.txt            ← Project dependencies
├── README.md                   ← Overview and setup instructions for the user.


