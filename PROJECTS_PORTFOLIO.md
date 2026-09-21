# 🌟 Engineering Portfolio & Project Knowledge Base
### High-Priority Core Projects for Autonomous Resume Generation & ATS Matching

> **System Notice:** This document is the **authoritative Grounding Corpus** and source of truth for the Resume Generation Agent. Every claim, metric, technology token, and architectural detail documented here is verified directly from the project source repositories and README specifications.

---

## 📊 Quick Reference & Priority Matrix

| Project | Domain | Priority | Links & Demos | Primary Tech Stack | Key Benchmark / Metric | Recognition |
|---|---|:---:|---|---|---|---|
| **Aegis Forge** | AI/ML, Voice Agents | **P0 (High)** | [GitHub](https://github.com/UtkarshSingh-09/Aegis-Forge-Agents) • [Demo Video](https://youtu.be/6XJ7HiaCKKQ) | Python, FastAPI, LiveKit, Groq (Llama 3.1/3.3), Deepgram Nova-3, Next.js 16 | **~850ms** voice round-trip latency, **6** concurrent agents | **1st Runner-Up** · Zenith National Hackathon ($1,500 Prize) |
| **Trinetra** | Fintech, Vector Search | **P0 (High)** | [GitHub](https://github.com/UtkarshSingh-09/Trinetra-Agent) • **Patent Filed** | Python, FastAPI, Qdrant (14 collections), Groq 70B, Redis, React 19 | **60-second** credit underwriting, **14** agents × 14 collections | **Patent Filed** · Qdrant Underwriting Innovation |
| **RudraKernel** | Reinforcement Learning | **P0 (High)** | [GitHub](https://github.com/UtkarshSingh-09/RudraKernel) • [Live HF Space](https://huggingface.co/spaces/UtkarshSingh09/RudraKernel-env) | Python, OpenEnv, TRL, Unsloth, LoRA, GRPO, FastAPI, Gradio | **9-component** R1–R9 reward system, **8** NPC agents | **Top Finalist** · Meta OpenEnv × PyTorch Hackathon 2026 |
| **MerchantMind** | Agentic Commerce | **P0 (High)** | [GitHub](https://github.com/UtkarshSingh-09/MerchentMind-) • [Live Demo](https://merchantmind-ai.netlify.app) • [Demo Video](https://youtu.be/hS77jr1y1z4) | Python 3.12, FastAPI, PostgreSQL 16, Redis 7, Razorpay SDK, Deepgram Flux | **<650ms** ReAct loop, 2PC distributed saga, **151** tests | **Track 01** · Razorpay AI Buildathon 2026 |
| **AstraGuard** | Behavioral Fintech | **P1** | [GitHub](https://github.com/UtkarshSingh-09/AstraGuard) • [Live Demo](https://astra-guard.vercel.app/) | Python 3.13+, FastAPI, LangGraph, MongoDB, Redis, ChromaDB, Twilio | Deterministic FIRE & Tax engines, Form 16/CAS parser | Team CodeHashiras · Behavioral Interventions |
| **Madad AI** | Offline Mesh Networks | **P1** | [GitHub](https://github.com/UtkarshSingh-09/MadadAI) | Python 3.8+, Streamlit, PyTorch, Qdrant, Raw Sockets (TCP/UDP), AES-128 | Tri-Link (Wi-Fi/BLE/LoRa), Store-and-Forward DTN | Open-Source Humanitarian Disaster Response |

---

## 🛡️ Project 1 (P0): Aegis Forge
### *Hyper-Realistic Multi-Agent AI Interview Simulation & FAANG-Grade Evaluation*

* **GitHub Repository:** [`github.com/UtkarshSingh-09/Aegis-Forge-Agents`](https://github.com/UtkarshSingh-09/Aegis-Forge-Agents) (also [`AegisForge`](https://github.com/UtkarshSingh-09/AegisForge))
* **Demo Video (YouTube Walkthrough):** [`youtu.be/6XJ7HiaCKKQ`](https://youtu.be/6XJ7HiaCKKQ)
* **Team:** Code Hashiras
* **Accolades:** **1st Runner-Up · Zenith National Hackathon · $1,500 Prize**
* **Domains:** AI/ML · WebRTC Voice · Distributed Agents · Cybersecurity & OSINT · Full-Stack

```
                            ┌─────────────────────────────────────────────────────┐
                            │            AEGIS FORGE MULTI-AGENT ENGINE           │
                            └─────────────────────────────────────────────────────┘
                                                       │
                      ┌────────────────────────────────┼────────────────────────────────┐
                      ▼                                ▼                                ▼
            ┌──────────────────┐             ┌──────────────────┐             ┌──────────────────┐
            │  🎙️ Incident Lead │             │  ⚡ Pressure Agent│             │  👁️ Observer     │
            │  LiveKit Voice   │             │  Urgent alerts   │             │  Silent grader   │
            │  Groq Llama 3.1  │             │  Data channel    │             │  6-axis FAANG    │
            └─────────┬────────┘             └─────────┬────────┘             └─────────┬────────┘
                      │                                │                                │
                      └────────────────────────────────┼────────────────────────────────┘
                                                       ▼
                      ┌────────────────────────────────┼────────────────────────────────┐
                      ▼                                ▼                                ▼
            ┌──────────────────┐             ┌──────────────────┐             ┌──────────────────┐
            │  🕵️ Mole Agent   │             │  🛡️ Governor     │             │  🚨 Crisis Popup │
            │  Integrity traps │             │  Safety guard    │             │  Surprise tests  │
            │  Bypasses/cheats │             │  Human handover  │             │  Code to Monaco  │
            └──────────────────┘             └──────────────────┘             └──────────────────┘
```

### 1. System Architecture & Capabilities
* **6-Agent Coordinated System:** Operates 6 autonomous, simultaneous AI agents working in concert rather than a single chatbot:
  1. **🎙️ Incident Lead:** Drives a structured 4-phase FAANG-style technical interview (Introduction, Project Deep-Dive, Live Coding, Wrap-Up), pushing questions directly into a collaborative Monaco Code Editor.
  2. **⚡ Pressure Agent:** Simulates an anxious executive stakeholder injecting unpredictable urgency via LiveKit WebRTC data channels every 15–40 seconds (50% activation probability).
  3. **👁️ Observer Agent:** Asynchronously grades every candidate utterance across a 6-dimensional FAANG rubric using Groq Llama 3.3-70B-versatile.
  4. **🕵️ Mole Agent:** Tests moral and engineering integrity by offering unethical shortcuts (e.g., "bypass security logging") via screen popups every 45–90 seconds.
  5. **🛡️ Governor Agent:** Safety supervisor monitoring content, toxic keywords, and low-confidence streaks (triggering human takeover on 3+ failures).
  6. **🚨 Crisis Popup Agent:** Injects live production outages at 2.5 min and 9.5 min marks, pushing broken code directly into the candidate's IDE.
* **Sub-Second Voice Pipeline:** Built on **LiveKit WebRTC Agents** coupled with **Deepgram Nova-3 STT/TTS**, sustaining round-trip voice latency of **~850ms**.
* **Resume OSINT & GitHub Trust Verification:** Extracts candidate skills via `pdfplumber` and OCR, cross-checks claimed skills against the candidate's live GitHub repositories via GitHub REST API, and calculates an algorithmic **Trust Score** (50 base + 10 LinkedIn + 20 GitHub + 20 skill verification ratio).
* **DQI (Decision Quality Index) & FSIR Report:** Computes a 10-point DQI across 6 competency axes (*Communication, Problem Solving, Technical Competency, Testing & Edge Cases, System Design, Crisis Management*), rendering an automated **Full-Spectrum Interview Report (FSIR)** PDF complete with MediaPipe proctoring metrics (eye contact, posture, fluency).

### 2. Verified Technical Stack
* **Backend:** Python 3.11+, FastAPI, Uvicorn, Pydantic v2, `pdfplumber`, `structlog`
* **Agent & Voice:** LiveKit Agents SDK, WebRTC, Deepgram Nova-3 (STT/TTS), Groq SDK (Llama 3.1 8B, Llama 3.3 70B)
* **Frontend:** Next.js 16 (App Router), React, TypeScript, Tailwind CSS, Monaco Editor, Framer Motion, GSAP
* **Computer Vision / Proctoring:** Google MediaPipe (face mesh, eye gaze tracking, posture anomaly detection)

### 3. Golden Grounding Metrics & Bullets
* **Latency:** ~850ms round-trip voice interaction latency.
* **Scale:** 6 concurrent coordinated agents per session across 40-minute simulation intervals.
* **Trust Scoring:** Deterministic mathematical formulation combining GitHub OSINT and resume claim verification.
* **Evaluation Fidelity:** Automated 6-axis competency spider radar with 4-tier decision outputs (Strong Hire, Hire, Lean Hire, No Hire).

---

## 🔱 Project 2 (P0): Trinetra
### *Agentic Commercial Credit Intelligence OS Powered by Qdrant Vector DB*

* **GitHub Repository:** [`github.com/UtkarshSingh-09/Trinetra-Agent`](https://github.com/UtkarshSingh-09/Trinetra-Agent) (also [`Trinetra-V2.O`](https://github.com/UtkarshSingh-09/Trinetra-V2.O))
* **Intellectual Property:** **Patent Filed** (`Trinetra — Cross Compliance Guardian`)
* **Accolades:** Designed for Qdrant Underwriting Innovation Challenge (Solves ₹152T credit gap)
* **Domains:** Fintech · Vector Search · Agentic Workflows · Explainable AI (XAI) · Edge/Local-First

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 TRINETRA VECTOR OS                                     │
├────────────────────────────────────────────────────────────────────────────────────────┤
│  14 Specialized AI Agents          │  14 Dedicated Qdrant Vector Collections           │
├────────────────────────────────────┼───────────────────────────────────────────────────┤
│  • compliance-agent (AML/KYC)      │  1. document_chunks       8. mca_filings          │
│  • doc-agent (OCR & Ratios)        │  2. financial_profiles    9. pan_profiles         │
│  • gst-agent (Circular Trading)    │  3. gst_patterns         10. risk_decisions       │
│  • bank-recon-agent (Recon)        │  4. bank_recon_profiles  11. pd_transcripts       │
│  • mca-agent (Corporate Filings)   │  5. news_articles        12. stress_scenarios     │
│  • web-agent (RAG & Litigation)    │  6. litigation_records   13. audit_events         │
│  • pan-agent (SurePass KYC)        │  7. rbi_circulars        14. application_summaries│
│  • model-selector-agent            │                                                   │
│  • risk-agent (SHAP/LIME)          │  • 384-dimensional all-MiniLM-L6-v2 embeddings    │
│  • bias-agent (Fairness audit)     │  • Native payload filtering & hybrid vector search│
│  • stress-agent (DSCR Shock)       │  • Sub-50ms query latency via HTTP port 6333      │
│  • pd-agent (Transcript NLP)       │  • 100% offline & local Docker privacy-safe       │
│  • cam-agent (10-Page Word CAM)    │                                                   │
│  • monitor-agent (Drift/Health)    │                                                   │
└────────────────────────────────────┴───────────────────────────────────────────────────┘
```

### 1. System Architecture & Capabilities
* **Full Lifecycle Underwriting in 60 Seconds:** Replaces traditional 3–5 day manual commercial loan underwriting workflows for India's ₹152 trillion credit market, processing complex filings (ITR, GSTR-2B/3B, MCA21, Bank Statements) in under 60 seconds.
* **14 AI Agents × 14 Qdrant Collections:** Employs a distributed multi-agent architecture where 14 specialized agents independently extract, verify, analyze, and persist financial intelligence into 14 isolated Qdrant vector collections.
* **Unified Credit Schema Object (UCSO):** Shared cross-agent data backbone spanning 18 distinct namespaces, synchronized via Redis Pub/Sub events and WebSocket state broadcasts.
* **Advanced Vector Operations & Hybrid Search:** Uses 384-dimensional embeddings (`sentence-transformers/all-MiniLM-L6-v2`) with Cosine distance. Implements single-query hybrid search combining semantic similarity with strict boolean metadata filtering (`status == 'FLAG'`, `discrepancy_pct >= 10.0`).
* **Fraud & Anomaly Detection:**
  * **GST Discrepancy & Circular Trading:** Reconciles GSTR-2B purchase logs against GSTR-3B tax returns to detect invoice inflation and carousel trading rings.
  * **Bank-GST Turnover Reconciliation:** Correlates real bank credit flows with declared GST turnovers to flag hidden liabilities.
  * **MCA21 Corporate Intelligence:** Cross-checks active director charges and legal defaults via MCA filings.
* **Explainable AI (XAI) & Stress Testing:** Combines XGBoost and LightGBM models with **SHAP** (top-5 feature importance) and **LIME** local interpretations, followed by counterfactual bias audits and macro DSCR stress testing under rate/revenue shocks.
* **Automated CAM Generation:** Generates a comprehensive 10-page Credit Appraisal Memorandum (CAM) Word document rendered via `docxtpl` across 110 dynamic tags.

### 2. Verified Technical Stack
* **Vector Database:** Qdrant Vector DB (14 collections, Docker containerized, HTTP port 6333)
* **Backend:** Python 3.11+, FastAPI, Uvicorn, Redis Pub/Sub, `docxtpl`, PyMuPDF, `pdfplumber`
* **Machine Learning & NLP:** `sentence-transformers`, `all-MiniLM-L6-v2`, XGBoost, LightGBM, SHAP, LIME, Groq Llama 3.3 70B
* **Frontend:** React 19, Vite, Framer Motion, Spline 3D, Axios, WebSockets, Vitest, Playwright

### 3. Golden Grounding Metrics & Bullets
* **Throughput:** Underwriting turnaround compressed from 3–5 business days to **60 seconds**.
* **Vector Scale:** 14 distinct Qdrant collections utilizing 384-dim dense vectors with sub-50ms retrieval latency.
* **Lines of Code:** Over 5,400+ lines of Python agent orchestration and API contracts.
* **Testing:** 100% test coverage target with Vitest unit tests and Playwright end-to-end browser journeys.

---

## 🛡️ Project 3 (P0): RudraKernel
### *LLM Reliability Infrastructure & Reinforcement Learning Environment for Sleeper-Agent Detection*

* **GitHub Repository:** [`github.com/UtkarshSingh-09/RudraKernel`](https://github.com/UtkarshSingh-09/RudraKernel)
* **Live Interactive Demo (Hugging Face Space):** [`huggingface.co/spaces/UtkarshSingh09/RudraKernel-env`](https://huggingface.co/spaces/UtkarshSingh09/RudraKernel-env)
* **Accolades:** **Top Finalist · Meta OpenEnv × PyTorch Hackathon 2026** (OpenEnv India 2026)
* **Domains:** Reinforcement Learning · Multi-Agent Safety · Adversarial Defense · Epistemic Resilience

```
                                  ┌────────────────────────────────┐
                                  │      SIEGE ENVIRONMENT         │
                                  │  (OpenEnv reset / step / state)│
                                  └───────────────┬────────────────┘
                                                  │
                         ┌────────────────────────┴────────────────────────┐
                         ▼                                                 ▼
             ┌───────────────────────┐                         ┌───────────────────────┐
             │   8 NPC AGENT POOL    │                         │    DEFENDER LLM       │
             │   Cooperative Trust   │ ── Adversarial Flip ──▶ │    MCP Tool Actions:  │
             │   Belief Mutation     │                         │    • diagnose         │
             │   Whisper & Cascades  │                         │    • challenge        │
             │   Red-Herring Noise   │                         │    • ratify / escalate│
             └───────────────────────┘                         └───────────┬───────────┘
                                                                           │
                                                                           ▼
                                                               ┌───────────────────────┐
                                                               │  GROUND-TRUTH REWARDS │
                                                               │  R1: Resolution (30%) │
                                                               │  R2: Resistance (25%) │
                                                               │  R3: Detection (20%)  │
                                                               │  R4: Trust Calib (10%)│
                                                               │  R5: Confidence (7%)  │
                                                               │  R6: Efficiency (4%)  │
                                                               │  R7: Postmortem (2%)  │
                                                               │  R8: Severity-Spd (1%)│
                                                               │  R9: Correlation (1%) │
                                                               └───────────────────────┘
```

### 1. System Architecture & Capabilities
* **Epistemic Cascade Failure Mitigation:** Specifically tackles the vulnerability where high-trust collaborative agents turn malicious and propagate falsified beliefs through an agent coalition (analogous to biological immune systems battling pathogens).
* **SIEGE Multi-Agent Environment:** Built strictly to the **OpenEnv standard specification** (`reset()`, `step()`, `state()`), simulating 8 autonomous NPC agents with dynamic trust scores, private whisper channels, and deceptive red-herrings.
* **9-Component Composable Ground-Truth Reward System (R1–R9):** Eliminates subjective LLM-as-a-judge scoring by computing rewards directly from mathematical and deterministic environment state:
  * **R1 Resolution (30%):** Accuracy in diagnosing true underlying root causes.
  * **R2 Deception Resistance (25%):** Resistance against sleeper agent misinformation.
  * **R3 Detection (20%):** Precision and recall in identifying rogue claims without false positives.
  * **R4 Trust Calibration (10%):** Mathematical alignment of internal trust vectors with factual reliability.
  * **R5 Confidence Calibration (7%):** Penalizes overconfident inaccuracies.
  * **R6 Temporal Efficiency (4%):** Step-wise penalties for latency in decision making.
  * **R7 Postmortem Quality (2%):** Causal and actionable retrospective accuracy.
  * **R8 Severity-Speed (1%):** Exponential speedup incentives under critical system emergencies.
  * **R9 Correlation (1%):** Cross-signal verification filtering out planted red-herring anomalies.
* **Fine-Tuning with GRPO:** Includes production training pipelines utilizing **Group Relative Policy Optimization (GRPO)** via Unsloth, Hugging Face TRL, and LoRA adapters for defense policy distillation.
* **Deterministic Replay & Failure Taxonomy:** Formalizes 4 distinct epistemic failure modes (*Epistemic Cascade, Sleeper Activation, Self-Cascade, Belief Mutation*) with $R_0$ belief spread metrics, belief half-life, and entropy tracking.
* **Interactive Command Console:** Deployed on Hugging Face Spaces featuring a comprehensive Gradio War Room (Incident Command, Before-After comparisons, Arms Race learning curves).

### 2. Verified Technical Stack
* **Core & Environment:** Python 3.10+, OpenEnv Specification, FastAPI, Uvicorn, Pydantic v2
* **Reinforcement Learning:** Hugging Face TRL, Unsloth, LoRA, PyTorch, GRPO training loops
* **Frontend / Analytics:** Gradio Interactive Dashboard, Matplotlib, Seaborn
* **Quality & Validation:** Pytest, Ruff, Mypy, deterministic seed replay engine

### 3. Golden Grounding Metrics & Bullets
* **Reward Formulation:** 9 composable ground-truth components (R1–R9) with zero LLM-judge subjectivity.
* **Agent Simulation:** 8 active NPC agents operating under cooperative-to-adversarial role flip scenarios.
* **Standard Compatibility:** Full OpenEnv specification compliance with containerized environment interfaces.
* **Deployment:** Public live deployment on Hugging Face Spaces (`UtkarshSingh09/RudraKernel-env`).

---

## 🛒 Project 4 (P0): MerchantMind
### *Autonomous Conversational Commerce & Razorpay-Native Agentic Growth Engine*

* **GitHub Repository:** [`github.com/UtkarshSingh-09/MerchentMind-`](https://github.com/UtkarshSingh-09/MerchentMind-)
* **Live Storefront Demo:** [`merchantmind-ai.netlify.app`](https://merchantmind-ai.netlify.app)
* **Demo Video (YouTube Walkthrough):** [`youtu.be/hS77jr1y1z4`](https://youtu.be/hS77jr1y1z4)
* **Accolades:** **Track 01 · AI Growth & Agentic Commerce · Razorpay AI Buildathon 2026**
* **Domains:** E-Commerce · Multi-Agent Concierge · Financial Transactions · Speech AI · Concurrency

```
                        ┌────────────────────────────────────────────────────────┐
                        │              MERCHANTMIND REASONING PIPELINE           │
                        └────────────────────────────────────────────────────────┘
                                                    │
                ┌───────────────────────────────────┼───────────────────────────────────┐
                ▼                                   ▼                                   ▼
      ┌──────────────────┐                ┌──────────────────┐                ┌──────────────────┐
      │  🎙️ Speech Engine │                │  🛡️ Guardrails   │                │  🤖 Agents       │
      │  Deepgram Flux   │                │  0ms Regex Budget│                │  AgentRouter (8B)│
      │  Phonetic Normal.│ ─────────────▶ │  NFKC Sanitizer  │ ─────────────▶ │  Discovery (70B) │
      │  Indian Localities│                │  Store Isolation │                │  Shopping (70B)  │
      └──────────────────┘                └──────────────────┘                └─────────┬────────┘
                                                                                        │
                                                                                        ▼
                                                                              ┌──────────────────┐
                                                                              │ ⚡ 2PC Saga       │
                                                                              │ Phase 1: Row-Lock│
                                                                              │ Phase 2: Razorpay│
                                                                              │ Phase 3: Commit  │
                                                                              └──────────────────┘
```

### 1. System Architecture & Capabilities
* **Conversational Commerce Concierge:** Converts passive, high-friction e-commerce catalogs into an intelligent conversational sales agent capable of understanding vague intents (e.g., *"I need an eggless birthday cake under ₹700 in Indiranagar"*), querying 200+ local Bangalore stores in **<650ms**.
* **Specialized Multi-Agent Orchestration:**
  * **AgentRouter (Groq Llama 3.1 8B):** Ultra-low-latency intent classifier.
  * **DiscoveryAgent (Groq Llama 3.3 70B):** Cross-catalog multi-store semantic matching with geographic proximity sorting.
  * **ShoppingAgent (Groq Llama 3.3 70B):** In-store cart management with occasion-aware upselling (e.g., pairing birthday candles only when total cart stays within user's declared budget).
  * **MerchantAgent:** Backend business intelligence for stock turnover analysis and lapsed-shopper re-engagement campaigns.
* **3-Phase Distributed Checkout Saga (Two-Phase Commit):**
  * **Phase 1 (Stock Lock):** Acquires pessimistic database row locks (`SELECT ... FOR UPDATE`) in PostgreSQL 16 to guarantee zero flash-sale overselling.
  * **Phase 2 (Razorpay Gateway):** Communicates with Razorpay Orders & Payment Links API with exact integer paise calculations (`int(round(amount * 100))`).
  * **Phase 3 (Commit & Audit):** Transitions orders to `pending_payment` with an immutable audit event trail.
  * **Automated Rollback Compensation:** Immediately reverts stock reservations and marks orders failed if payment link generation or network calls fault.
* **Raw-Byte HMAC-SHA256 Webhook Capture:** Secures payment verification against payload tampering and replay attacks using raw request byte hashing.
* **Ambient Indian English Voice Engine:** Integrates **Deepgram Flux Meena** (`flux-meena-en`) with a customized phonetic dictionary for Bangalore localities (*Indiranagar, Koramangala, HSR, Whitefield*) and culinary items (*Biryani, Paneer, Gulab Jamun*), featuring adaptive 2.2s–3.0s silence auto-dispatch and instant voice barge-in.
* **Deterministic Guardrail Layer:** Hard mathematical budget limiter (`cart_total + upsell <= user_budget`), NFKC Unicode deobfuscation, and zero-width prompt injection sanitizers.

### 2. Verified Technical Stack
* **Backend:** Python 3.12, FastAPI 0.115, Uvicorn, PostgreSQL 16 (Pessimistic Locks), Redis 7 (Sliding Window Rate Limiter & Idempotency)
* **AI & Voice:** Groq SDK (Llama 3.3 70B & Llama 3.1 8B), Deepgram Voice API (Flux Meena), Web Speech API
* **Payment:** Razorpay Python SDK (Orders API, Payment Links API, Webhooks HMAC verification)
* **Frontend:** Next.js 16 (App Router), React, TypeScript, Tailwind CSS, Three.js, Lucide Icons, Netlify Edge
* **Testing:** Comprehensive **151-test suite matrix** across unit, integration, and security guardrails

### 3. Golden Grounding Metrics & Bullets
* **Latency:** Sub-650ms ReAct reasoning and search loop across 200+ local Bangalore stores.
* **Concurrency:** Pessimistic row-level locking (`SELECT ... FOR UPDATE`) eliminating inventory race conditions.
* **Integrity:** 100% mathematically bounded budget enforcement with automated 2PC saga rollback compensation.
* **Reliability:** 151 automated test cases verifying deterministic guardrails and webhook security.

---

## 🛡️ Project 5 (P1): AstraGuard
### *Behavioral Financial Intelligence Platform with Deterministic Calculation Engines*

* **Repository:** `github.com/UtkarshSingh-09/AstraGuard` (Team CodeHashiras)
* **Live Demo:** `astra-guard.vercel.app`
* **Domains:** Fintech · Behavioral Finance · LangGraph Agents · Regulatory Compliance

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 ASTRAGUARD PLATFORM                                    │
├────────────────────────────────────────────────────────────────────────────────────────┤
│  Core Architectural Principle:                                                         │
│  "LLMs explain, classify, narrate, and intervene.                                      │
│   Deterministic Python code performs the financial math."                              │
├────────────────────────────────────────────────────────────────────────────────────────┤
│  • Deterministic Engines:                                                              │
│    - FIRE Planner (SIP optimization, emergency fund, target retirement corpus)         │
│    - Tax Optimizer (Old vs New regime deduction comparison)                            │
│    - Portfolio X-Ray (Fund & portfolio XIRR, mutual fund overlap, expense drag)         │
│  • Behavioral Guard:                                                                   │
│    - Market panic detection & proactive intervention workflows                         │
│    - Multi-channel escalation via WebSockets and Twilio WhatsApp alerts                │
│  • Ingestion Pipelines:                                                                │
│    - Automated PDF extraction for Form 16 and CAS (Consolidated Account Statements)   │
│  • Compliance & RAG:                                                                   │
│    - ChromaDB vector store indexing SEBI regulatory text for audit-guarded narration   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### 1. System Architecture & Capabilities
* **Strict Separation of Concerns:** Enforces a rigid engineering boundary: stochastic LLMs handle conversational onboarding, risk explanation, and behavioral panic interventions, while deterministic Python engines execute all financial computations (FIRE targets, tax liabilities, XIRR).
* **Automated Document Ingestion:** Custom parsing pipelines extracting structured payroll and mutual fund holdings from **Form 16** tax forms and **CAS (Consolidated Account Statements)**.
* **Behavioral Panic Intervention:** Analyzes user behavioral risk profile during market volatility; if a user threatens to panic-pause SIPs, the system models real multi-year financial loss and triggers multi-channel intervention alerts via WebSockets and Twilio WhatsApp messaging.
* **Compliance RAG:** Leverages ChromaDB to index SEBI circulars and financial regulations, ensuring AI-generated advice strictly adheres to compliance guardrails without hallucinated financial guarantees.

### 2. Verified Technical Stack
* **Backend:** Python 3.13+, FastAPI, Uvicorn, LangGraph, MongoDB, Redis, ChromaDB, Twilio SDK
* **Frontend:** Next.js / React, Tailwind CSS, Vercel deployment
* **Document Processing:** PyMuPDF, pdfplumber, specialized CAMS/Form 16 regex pipelines

---

## 🆘 Project 6 (P1): Madad AI
### *Resilient Offline Mesh Network & Delay-Tolerant Disaster Communication System*

* **Repository:** `github.com/UtkarshSingh-09/MadadAI`
* **Status:** Open-Source Humanitarian Project
* **Domains:** Offline Mesh Networks · Delay-Tolerant Networking (DTN) · Socket Systems · Vector Triage · Cryptography

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                MADAD AI DTN ARCHITECTURE                               │
├────────────────────────────────────────────────────────────────────────────────────────┤
│   SURVIVOR APP (Victim)              MULE NODE (Ferry Router)          COMMAND HQ      │
│  ┌───────────────────────┐          ┌───────────────────────┐    ┌───────────────────┐ │
│  │ Encrypt SOS (AES-128) │          │ Dual Port Listeners:  │    │ Qdrant Cloud DB   │ │
│  │ GPS / Audio / Image   │ ──WiFi/─▶│ • 6008: Uplink SOS    │─▶  │ Semantic Triage   │ │
│  │ UDP Beacon Broadcast  │   BLE    │ • 6009: Downlink Reply│    │ Folium Heatmap    │ │
│  └───────────────────────┘          └───────────┬───────────┘    └─────────┬─────────┘ │
│             ▲                                   │                          │           │
│             │                                   ▼                          ▼           │
│             │                        Courier Bag (mule_inbox) ◀─── Rescue Orders JSON  │
│             └────── Download Orders ────────────┘                                      │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### 1. System Architecture & Capabilities
* **Zero-Connectivity Disaster Communication:** Solves catastrophic infrastructure breakdown during natural disasters (earthquakes, floods) or war zones by turning standard laptops/smartphones into an offline peer-to-peer mesh network without cellular or internet access.
* **Store-and-Forward DTN (Delay-Tolerant Networking):** Implements a "Ferry-Based" transport protocol where moving volunteers/boats ("Mules") physically transport encrypted data packets between isolated danger zones and cloud-connected command stations.
* **Tri-Link Adaptive Protocol:** Intelligently arbitrates packet routing across three wireless physical layers: **Wi-Fi**, **Bluetooth Low Energy (BLE)**, and **LoRa (Meshtastic)**.
* **Dual-Port Socket Engine:**
  * **Port 6008 (Uplink):** Raw asynchronous TCP/UDP socket listener receiving encrypted survivor SOS beacons.
  * **Port 6009 (Downlink):** Dispatches cached command orders (`GET_MAIL:{My_ID}`) from HQ back to trapped survivors upon re-entering disaster perimeters.
* **Semantic Triage via Qdrant Cloud:** Vectors uploaded by mules are indexed in Qdrant Vector DB, enabling incident command personnel to execute semantic queries (e.g., *"Find medical emergencies with rising flood waters"*) alongside geospatial Folium heatmaps.
* **Blind Courier Cryptography:** All packets are end-to-end encrypted using **AES-128 (Fernet)** before leaving survivor devices; Mule nodes operate as blind forwarders unable to inspect SOS contents or rescue orders.

### 2. Verified Technical Stack
* **Networking & Transport:** Python 3.8+, Raw Sockets (TCP/UDP), Python `asyncio`, Socket.io, Wi-Fi Direct, BLE, LoRa
* **Security & Cryptography:** AES-128 (Fernet symmetric encryption), UUID-based anonymous identifiers
* **Cloud & Visualization:** Qdrant Cloud (Vector DB for semantic triage), Streamlit, Folium, Plotly, PyTorch

### 3. Golden Grounding Metrics & Bullets
* **Networking:** Dual-port (6008/6009) asynchronous socket architecture with store-and-forward delay tolerance.
* **Security:** 100% blind-courier AES-128 encryption guaranteeing zero intermediate data tampering.
* **Search & Triage:** Natural language semantic triage across disaster reports powered by Qdrant vector similarity.

---

## 🗃️ Skills & Keyword Gazetteer Matrix
*(For use by the `validate/keywords.py` and `writer/verify.py` modules to ensure 100% grounded technical matching)*

### Languages & Runtimes
`Python` (3.8, 3.10, 3.11, 3.12, 3.13), `TypeScript`, `JavaScript`, `SQL`, `LaTeX`, `HTML5`, `CSS3`, `Node.js`

### Frameworks & Libraries
`FastAPI`, `Uvicorn`, `Streamlit`, `Next.js 16`, `React 19`, `LangGraph`, `LiveKit Agents`, `LiveKit WebRTC`, `Deepgram SDK`, `Razorpay SDK`, `Pydantic v2`, `Jinja2`, `Tailwind CSS`, `Framer Motion`, `GSAP`, `Three.js`, `Monaco Editor`, `MediaPipe`, `PyMuPDF`, `pdfplumber`, `docxtpl`, `structlog`, `tenacity`, `httpx`, `Socket.io`, `Folium`, `Plotly`

### Databases, Caches & Vector Engines
`Qdrant Vector DB` (14 collections, hybrid search, HTTP 6333, Qdrant Cloud), `PostgreSQL 16` (row locks, 2PC saga), `Redis 7` (Pub/Sub, sliding window rate limits, idempotency), `SQLite` (WAL mode), `MongoDB`, `ChromaDB`

### Machine Learning, RL & Explainability
`all-MiniLM-L6-v2`, `BAAI/bge-small-en-v1.5`, `sentence-transformers`, `XGBoost`, `LightGBM`, `SHAP`, `LIME`, `OpenEnv`, `Hugging Face TRL`, `Unsloth`, `LoRA`, `GRPO (Group Relative Policy Optimization)`, `PyTorch`

### LLM Inference & Models
`Groq`, `Llama 3.1 8B`, `Llama 3.3 70B`, `Llama-3.3-70b-versatile`, `Anthropic Claude 3.5 / 3.7 / 4.6 Sonnet`, `Deepgram Nova-3`, `Deepgram Flux Meena (flux-meena-en)`

### Architectural & Systems Concepts
`Multi-Agent Systems`, `Two-Phase Commit (2PC) Distributed Saga`, `Pessimistic Row-Level Locking (SELECT ... FOR UPDATE)`, `HMAC-SHA256 Signature Verification`, `WebSockets`, `Redis Pub/Sub`, `Sub-Second Voice WebRTC`, `Epistemic Cascade Failure`, `Sleeper-Agent Detection`, `Ground-Truth Reward Engineering (R1–R9)`, `Deterministic Replay`, `Explainable AI (XAI)`, `Counterfactual Bias Audit`, `DSCR Stress Testing`, `CAM Report Generation`, `Form 16 & CAS PDF Parsing`, `Deterministic Financial Math Engine`, `Delay-Tolerant Networking (DTN)`, `Store-and-Forward Mesh`, `Raw Socket Programming (TCP/UDP)`, `AES-128 Fernet Encryption`, `Blind Courier Cryptography`

---

## 🎯 Resume Agent Integration Mapping
*(Pre-configured for `data/config/projects_override.yaml`)*

```yaml
# data/config/projects_override.yaml
projects:
  - repo_name: "AegisForge"
    display_name: "Aegis Forge — Multi-Agent Technical Interview Simulator"
    include: true
    priority: 1
    tier: "P0"
    target_roles: ["AI/ML Engineer", "SDE", "Backend Engineer", "Full Stack Engineer", "Systems Engineer"]
    manual_notes: >
      Won 1st Runner-Up at Zenith National Hackathon ($1,500 prize). Built 6-agent simulation
      (Incident Lead, Pressure Agent, Observer, Mole, Governor, Crisis Popup). Integrated LiveKit
      WebRTC with Deepgram Nova-3 STT/TTS achieving ~850ms round-trip voice latency. Implemented
      GitHub OSINT verification with algorithmic Trust Scoring and automated 6-axis FAANG DQI scoring
      with PDF report generation. Next.js 16, Monaco Editor, Google MediaPipe proctoring.

  - repo_name: "Trinetra-V2.O"
    display_name: "Trinetra — Agentic Commercial Credit Intelligence OS"
    include: true
    priority: 2
    tier: "P0"
    target_roles: ["Backend Engineer", "Fintech SDE", "Data Engineer", "AI/ML Engineer"]
    manual_notes: >
      Automates commercial credit underwriting from 3-5 days to 60 seconds. Designed 14 AI agents
      interacting across 14 dedicated Qdrant vector collections (384-dim all-MiniLM-L6-v2, sub-50ms search).
      Engineered GST circular trading and bank reconciliation fraud detection algorithms. Implemented
      XGBoost/LightGBM risk models with SHAP/LIME explainability and automated 10-page Word CAM report
      generation with 110 dynamic tags. Over 5,400+ lines of Python; 100% test coverage target.

  - repo_name: "RudraKernel"
    display_name: "RudraKernel — Multi-Agent RL LLM Reliability Infrastructure"
    include: true
    priority: 3
    tier: "P0"
    target_roles: ["AI Safety Researcher", "RL/ML Engineer", "Backend Systems Engineer"]
    manual_notes: >
      Built for OpenEnv India 2026; live on Hugging Face Spaces. Developed multi-agent RL environment
      (SIEGE) tackling epistemic cascade failures and sleeper-agent deception across 8 NPC agents.
      Engineered 9 composable ground-truth reward components (R1-R9) with zero LLM-as-a-judge bias.
      Trained defense policies via GRPO using Unsloth, Hugging Face TRL, and LoRA. Implemented
      Gradio command console and deterministic replay engine with mathematical R0 spread tracking.

  - repo_name: "MerchentMind-"
    display_name: "MerchantMind — Autonomous Conversational Commerce & Razorpay Engine"
    include: true
    priority: 4
    tier: "P0"
    target_roles: ["SDE", "Backend Engineer", "Full Stack Engineer", "Payment Systems Engineer"]
    manual_notes: >
      Developed for Razorpay AI Buildathon 2026 (Track 01). Built multi-agent commerce concierge
      (Llama 3.3 70B & 3.1 8B on Groq) achieving <650ms ReAct loop across 200+ Bangalore stores.
      Engineered native Razorpay 3-Phase Distributed Checkout Saga (2PC) with PostgreSQL row locks
      (SELECT ... FOR UPDATE), automated stock rollback compensation, and raw HMAC-SHA256 webhook
      verification. Ambient Indian English voice engine via Deepgram Flux with custom phonetic dictionary.
      151 automated tests covering deterministic hard budget guardrails.

  - repo_name: "AstraGuard"
    display_name: "AstraGuard — Behavioral Financial Intelligence Platform"
    include: true
    priority: 5
    tier: "P1"
    target_roles: ["Full Stack Engineer", "Backend SDE", "Fintech Engineer"]
    manual_notes: >
      Architected financial platform strictly separating deterministic math engines (FIRE, Tax, XIRR)
      from LangGraph agentic reasoning. Engineered Form 16 and CAS PDF statement parsing pipelines.
      Implemented behavioral panic detection with automated Twilio WhatsApp and WebSocket intervention.
      ChromaDB vector RAG indexing SEBI compliance regulations.

  - repo_name: "MadadAI"
    display_name: "Madad AI — Resilient Offline Mesh Network & Disaster DTN"
    include: true
    priority: 6
    tier: "P1"
    target_roles: ["Systems Engineer", "Backend Engineer", "Distributed Systems Engineer", "Networks Engineer"]
    manual_notes: >
      Engineered delay-tolerant networking (DTN) disaster communication platform for zero-connectivity zones.
      Built store-and-forward physical mule routing with dual-port (6008 uplink / 6009 downlink) raw TCP/UDP
      sockets. Implemented blind-courier AES-128 Fernet encryption for victim privacy. Integrated Qdrant Cloud
      vector database for semantic disaster triage and Folium emergency geospatial heatmap visualization.
