<div align="center">

<img width="100%" src="assets/hero.svg" alt="Aegis Forge Hero" />

<br/>

`Forging Intelligence Under Pressure`<br/>
`Multi-Agent AI · Real-Time Voice · FAANG-Grade Evaluation · Resume OSINT`

<br/>

[![Python](https://img.shields.io/badge/Python-3.11+-D97706?style=for-the-badge&logo=python&logoColor=white&labelColor=151515)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-991B1B?style=for-the-badge&logo=fastapi&logoColor=white&labelColor=151515)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-16-FBBF24?style=for-the-badge&logo=next.js&logoColor=white&labelColor=151515)](https://nextjs.org)
[![LiveKit](https://img.shields.io/badge/LiveKit-Agents-D97706?style=for-the-badge&logo=webrtc&logoColor=white&labelColor=151515)](https://livekit.io)
[![Groq](https://img.shields.io/badge/Groq-Llama_3.1-991B1B?style=for-the-badge&labelColor=151515)](https://groq.com)
[![License](https://img.shields.io/badge/License-Proprietary-FBBF24?style=for-the-badge&labelColor=151515)](license.md)

<br/>

**1st Runner-Up · Zenith National Hackathon · $1,500 Prize**

</div>

<img width="100%" src="assets/divider.svg" alt="divider"/>

## `// system_overview`

<img width="100%" src="assets/metrics.svg" alt="Metrics" />

Aegis Forge is an AI-powered technical interview simulation platform that creates **hyper-realistic interview experiences** using a sophisticated **6-agent multi-agent system**. Unlike traditional chatbot-based mock interviews, Aegis Forge employs specialized AI agents working simultaneously — an Incident Lead driving conversation, a Pressure Agent injecting urgency, an Observer silently grading, a Mole testing integrity, a Governor ensuring safety, and Crisis Popups testing composure.

The system processes a candidate's resume, validates claims against **GitHub via OSINT**, generates personalized coding questions using **Groq LLM**, conducts a **real-time voice interview** via **LiveKit WebRTC + Deepgram STT/TTS**, and produces a comprehensive **FSIR (Full-Spectrum Interview Report)** with **DQI scoring** calibrated to FAANG hiring bars.

```bash
$ cat /etc/aegis/identity

SYSTEM      =  Aegis Forge
TYPE        =  Multi-Agent AI Interview Simulation Platform
AGENTS      =  6 Simultaneous  |  Autonomous  |  Coordinated
LATENCY     =  ~850ms Round-Trip  |  Sub-Second Voice
DOMAINS     =  AI/ML · DevOps · Cybersecurity · Blockchain · Backend · Frontend
OUTPUT      =  FSIR PDF Report  |  DQI Score  |  Competency Radar
TEAM        =  Code Hashiras
```

<img width="100%" src="assets/divider.svg" alt="divider"/>

## `// agent_architecture`

<img width="100%" src="assets/agents.svg" alt="Agent Architecture" />

<br/>

| Agent | Role | Behavior | Activation |
| :-- | :-- | :-- | :-- |
| **🎙️ Incident Lead** | Main Interviewer | Drives 4-phase FAANG interview with personalized coding questions | Continuous |
| **⚡ Pressure Agent** | Stressed Stakeholder | Random urgent interruptions via LiveKit data channel | Every 15–40s (50% chance) |
| **👁️ Observer Agent** | Silent Grader | Evaluates every turn using 6-dimension FAANG rubric | Every response |
| **🕵️ Mole Agent** | Integrity Tester | Offers unethical shortcuts via screen popups | Every 45–90s |
| **🛡️ Governor Agent** | Safety Monitor | Keyword detection + low-confidence streak monitoring | Continuous |
| **🚨 Crisis Popup** | Surprise Tester | Domain-specific crisis injection with code push to IDE | At 2.5min & 9.5min |

<img width="100%" src="assets/divider.svg" alt="divider"/>

## `// data_flow`

```
                    ┌─────────────────────────────────────────────────────┐
                    │                  CANDIDATE FLOW                     │
                    └─────────────────────────────────────────────────────┘

     ┌──────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
     │  Resume  │────▶│  Validation  │────▶│   Interview  │────▶│    Report    │
     │  Upload  │     │  + GitHub    │     │   Session    │     │  Generation  │
     │  (.pdf)  │     │  OSINT       │     │  (40 min)    │     │  (FSIR PDF)  │
     └──────────┘     └──────────────┘     └──────────────┘     └──────────────┘
          │                  │                     │                    │
          ▼                  ▼                     ▼                    ▼
     ┌──────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
     │ pdfplumber│     │  Groq LLM   │     │  6 Agents    │     │  DQI Score   │
     │ + OCR    │     │  GitHub API  │     │  LiveKit     │     │  PDF Export  │
     │          │     │  Trust Score │     │  Deepgram    │     │  Radar Chart │
     └──────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

<img width="100%" src="assets/divider.svg" alt="divider"/>

## `// interview_engine`

<details open>
<summary><b>[ 01 ] Incident Lead — The FAANG Interviewer</b></summary>

<br/>

The main voice agent that conducts a structured 4-phase technical interview, personalized from the candidate's resume.

| Phase | Duration | What Happens |
| :-- | :-- | :-- |
| **Phase 1 — Introduction** | 2 turns | Warm greeting by name, "tell me something NOT on your resume" |
| **Phase 2 — Projects Deep-Dive** | 2–3 turns | References specific resume projects, probes architecture decisions |
| **Phase 3 — Coding Challenges** | 60–70% | LLM-generated personalized questions with code blocks pushed to Monaco IDE |
| **Phase 3.5 — Quick Checks** | Between coding | 1-liner conceptual questions ("What does idempotent mean?") |
| **Phase 4 — Wrap-Up** | 2–3 turns | Specific feedback, candidate Q&A, professional close |

| Dimension | Detail |
| :-- | :-- |
| **Stack** | LiveKit Voice Agent · Groq Llama 3.1 · Deepgram Nova-3 STT/TTS |
| **Personalization** | Dynamic questions from resume skills, GitHub repos, detected field |
| **Adaptive** | Silently adjusts difficulty based on candidate performance |
| **Tools** | ToggleNotepad (push code to IDE), Crisis Trigger |

</details>

<details>
<summary><b>[ 02 ] Observer Agent — The Silent Evaluator</b></summary>

<br/>

Listens to every turn and produces structured JSON evaluations using a FAANG-calibrated 6-dimension rubric.

| Dimension | Rating Scale |
| :-- | :-- |
| **Communication** | Strong Hire (10) · Hire (7) · No Hire (3) · Strong No Hire (0) |
| **Problem Solving** | Same scale |
| **Technical Competency** | Same scale |
| **Testing & Edge Cases** | Same scale |
| **System Design** | Same scale |
| **Crisis Management** | Same scale |

| Dimension | Detail |
| :-- | :-- |
| **LLM** | Groq Llama 3.3-70b-versatile (separate model to split rate limits) |
| **Output** | Feeds DQI Calculator → FSIR Report |
| **Async** | All evaluations are non-blocking background tasks |

</details>

<details>
<summary><b>[ 03 ] Pressure Agent — The Stakeholder</b></summary>

<br/>

Simulates an anxious, non-technical stakeholder who interrupts with urgent demands.

| Dimension | Detail |
| :-- | :-- |
| **Trigger** | Random timer (15–40s intervals), 50% activation chance |
| **Examples** | "CEO on the line!", "Customers are tweeting!", "Make it green!" |
| **Delivery** | LiveKit data channel → Frontend alert popup |
| **Cooldown** | 20s initial grace period |

</details>

<details>
<summary><b>[ 04 ] Mole Agent — The Integrity Trap</b></summary>

<br/>

Offers unethical shortcuts to test candidate judgment under pressure.

| Dimension | Detail |
| :-- | :-- |
| **Trigger** | Background loop, every 45–90 seconds |
| **Tips** | Dynamic via Groq LLM ("Psst, bypass the logs…") |
| **Delivery** | `MOLE_POPUP` data packet → Frontend screen popup |
| **Tracking** | Bait accepted/rejected logged for FSIR integrity section |

</details>

<details>
<summary><b>[ 05 ] Governor Agent — The Safety Valve</b></summary>

<br/>

Continuous content moderation preventing harmful content and triggering human handover.

| Dimension | Detail |
| :-- | :-- |
| **Check 1** | High-risk keyword detection (real-time) |
| **Check 2** | Low confidence streak (3+ consecutive failures → handover) |
| **Threshold** | Confidence < 0.4 triggers warning |
| **Action** | Logs `SAFETY_INTERVENTION`, supports human takeover mode |

</details>

<details>
<summary><b>[ 06 ] Crisis Popup Agent — The Surprise Test</b></summary>

<br/>

Injects domain-specific crisis scenarios at strategic moments to test composure and problem-solving under sudden pressure.

| Dimension | Detail |
| :-- | :-- |
| **Timing** | Crisis #1 at 2.5 minutes, Crisis #2 at 9.5 minutes |
| **Generation** | Domain-specific via Groq LLM |
| **Delivery** | 1) Frontend popup  2) Agent context injection  3) Forced speech via `session.say()` |
| **Code Push** | If crisis contains code blocks → auto-pushed to Monaco IDE |

</details>

<img width="100%" src="assets/divider.svg" alt="divider"/>

## `// knowledge_engine`

The **AegisKnowledgeEngine** is a Singleton shared across the FastAPI backend and LiveKit agent process — the central intelligence layer that powers all agents.

```bash
$ cat /etc/aegis/knowledge_engine

PATTERN      =  Singleton (shared across processes)
RESUME       =  PDF Parse → LLM Skill Extraction → GitHub OSINT → Trust Score
INTEL        =  Dynamic Market Research via Groq (cached per field)
CONTEXT      =  Candidate profile injected into all agent prompts
FOCUS        =  Recruiter-selected topics from dashboard
MOLE_GEN     =  Context-aware integrity trap generation
```

| Capability | Implementation |
| :-- | :-- |
| **Resume Processing** | `pdfplumber` + OCR fallback → Groq skill extraction → GitHub API verification |
| **Trust Scoring** | 50 base + LinkedIn (10) + GitHub (20) + skill verification ratio (20) |
| **Market Intel** | Async Groq LLM generation with field-specific coding standards |
| **Focus Topics** | Recruiter dashboard → `focus_config.json` → agent prompt injection |
| **Dynamic Mole** | Context-aware tip generation from interview state |

<img width="100%" src="assets/divider.svg" alt="divider"/>

## `// scoring_system`

### DQI — Decision Quality Index

The proprietary scoring algorithm that aggregates all Observer evaluations into a single FAANG-calibrated score.

```
  ┌─────────────────────────────────────────────────────┐
  │              COMPETENCY RADAR (6-axis)               │
  │                                                      │
  │              Communication ─── 8                     │
  │             /                    \                    │
  │    Crisis ─── 7              9 ─── Problem Solving   │
  │             \                    /                    │
  │       System ─── 6          8 ─── Technical          │
  │               \            /                         │
  │                Testing ─── 7                         │
  │                                                      │
  │         Overall DQI: 7.5 / 10 → HIRE                │
  └─────────────────────────────────────────────────────┘
```

| Grade | Score | Meaning |
| :-- | :--: | :-- |
| **Strong Hire** | ≥ 8.5 | Exceptional across all dimensions |
| **Hire** | ≥ 7.0 | Meets the bar, solid fundamentals |
| **Lean Hire** | ≥ 5.5 | Borderline, potential observed |
| **Lean No Hire** | ≥ 4.0 | Significant gaps |
| **No Hire** | < 4.0 | Below hiring bar |

### FSIR — Full-Spectrum Interview Report

Auto-generated PDF containing:

| Section | Content |
| :-- | :-- |
| **Executive Block** | Decision, confidence %, primary reason |
| **Crisis Timeline** | Timestamped events with pressure handling scores |
| **DQI Breakdown** | Correct decisions, mistakes, critical misses |
| **Integrity Signals** | Mole interactions, resume claim consistency |
| **Communication Metrics** | Clarity, vocabulary, composure analysis |
| **Skill Validation** | Per-dimension alignment scores |
| **Agent Consensus** | All agent verdicts + panel confidence |
| **Competency Radar** | 6-axis spider chart |
| **MediaPipe Summary** | Eye contact, posture, fluency, cheating flags |

<img width="100%" src="assets/divider.svg" alt="divider"/>

## `// tech_stack`

<div align="center">

### Backend & AI
<img src="https://skillicons.dev/icons?i=python,fastapi&theme=dark&perline=8" />

<p>
  <img src="https://img.shields.io/badge/Groq-D97706?style=for-the-badge&labelColor=151515" />
  <img src="https://img.shields.io/badge/Llama_3.1-991B1B?style=for-the-badge&labelColor=151515" />
  <img src="https://img.shields.io/badge/Deepgram-FBBF24?style=for-the-badge&logo=deepgram&logoColor=white&labelColor=151515" />
  <img src="https://img.shields.io/badge/LiveKit_Agents-D97706?style=for-the-badge&logo=webrtc&logoColor=white&labelColor=151515" />
  <img src="https://img.shields.io/badge/Pydantic_v2-991B1B?style=for-the-badge&labelColor=151515" />
</p>

### Frontend
<img src="https://skillicons.dev/icons?i=nextjs,react,ts,tailwind&theme=dark&perline=8" />

<p>
  <img src="https://img.shields.io/badge/Monaco_Editor-D97706?style=for-the-badge&labelColor=151515" />
  <img src="https://img.shields.io/badge/Framer_Motion-991B1B?style=for-the-badge&labelColor=151515" />
  <img src="https://img.shields.io/badge/GSAP-FBBF24?style=for-the-badge&labelColor=151515" />
  <img src="https://img.shields.io/badge/MediaPipe-D97706?style=for-the-badge&logo=google&logoColor=white&labelColor=151515" />
</p>

### Infrastructure
<img src="https://skillicons.dev/icons?i=docker,git,github&theme=dark&perline=8" />

<p>
  <img src="https://img.shields.io/badge/LiveKit_Cloud-991B1B?style=for-the-badge&labelColor=151515" />
  <img src="https://img.shields.io/badge/UV_Package_Manager-FBBF24?style=for-the-badge&labelColor=151515" />
  <img src="https://img.shields.io/badge/Simli_Avatar-D97706?style=for-the-badge&labelColor=151515" />
</p>

### Resume Intelligence
<p>
  <img src="https://img.shields.io/badge/pdfplumber-D97706?style=for-the-badge&labelColor=151515" />
  <img src="https://img.shields.io/badge/Tesseract_OCR-991B1B?style=for-the-badge&labelColor=151515" />
  <img src="https://img.shields.io/badge/GitHub_API-FBBF24?style=for-the-badge&logo=github&logoColor=white&labelColor=151515" />
  <img src="https://img.shields.io/badge/ReportLab-D97706?style=for-the-badge&labelColor=151515" />
</p>

</div>

<img width="100%" src="assets/divider.svg" alt="divider"/>

## `// api_endpoints`

```bash
$ curl -s http://localhost:8000/ | jq .

{
  "status": "ok",
  "service": "aegis-forge-gateway"
}
```

| Method | Endpoint | Purpose |
| :-- | :-- | :-- |
| `POST` | `/upload-resume` | Upload PDF → validate → GitHub audit → field detection |
| `POST` | `/start-interview` | Create LiveKit room → dispatch agent → return join token |
| `POST` | `/api/set-focus-topics` | Recruiter-selected skills to deep-dive (max 5) |
| `POST` | `/api/set-candidate-role` | Manual override of auto-detected field |
| `GET` | `/candidate/{id}` | Retrieve candidate audit details |
| `GET` | `/download-report/{id}` | Download generated FSIR PDF |
| `POST` | `/mediapipe-metrics` | Receive behavioral biometrics from frontend |
| `GET` | `/mediapipe-metrics/{id}` | Retrieve stored MediaPipe data |

<img width="100%" src="assets/divider.svg" alt="divider"/>

## `// project_structure`

```
aegis-forge/
├── app/                          # LiveKit Agent Service
│   ├── main.py                   # Agent entry point & orchestration
│   ├── agents/                   # Multi-Agent System
│   │   ├── incident_lead.py      # Main FAANG interviewer
│   │   ├── pressure.py           # Stakeholder stress simulator
│   │   ├── observer.py           # Silent grading agent
│   │   ├── mole.py               # Integrity testing agent
│   │   ├── governor.py           # Safety monitoring agent
│   │   ├── crisis_popup.py       # Surprise crisis generator
│   │   ├── question_generator.py # Dynamic question generation
│   │   ├── prompts.py            # System prompt templates
│   │   ├── base.py               # Base agent class
│   │   └── tools.py              # Agent tools (ToggleNotepad)
│   ├── analysis/                 # Report Generation
│   │   ├── pipeline.py           # FSIR report orchestrator
│   │   ├── dqi_calculator.py     # DQI scoring algorithm
│   │   ├── pdf_generator.py      # PDF creation (ReportLab)
│   │   └── schemas.py            # Pydantic data models
│   ├── rag/                      # Scenario Management
│   │   ├── scenarios.json        # Interview scenario definitions
│   │   └── scenarios.py          # Scenario loader class
│   ├── resume/                   # Resume Processing
│   │   └── loader.py             # Field detection & context extraction
│   └── core/                     # Utilities
│       ├── end_detector.py       # End phrase detection
│       └── interview_timer.py    # Session timer (40 min)
│
├── backend/                      # FastAPI Backend
│   ├── main.py                   # API endpoints
│   ├── resume_validator.py       # PDF parsing + GitHub verification
│   ├── livekit_dispatch.py       # LiveKit room management
│   ├── funnel/
│   │   └── pipeline.py           # Knowledge Engine (Singleton)
│   └── core/
│       ├── state.py              # State machine
│       └── graph.py              # FSM graph builder
│
├── frontend/                     # Next.js Frontend
│   ├── app/                      # App Router pages
│   │   ├── interview/            # Interview UI
│   │   ├── dashboard/            # Recruiter dashboard
│   │   └── api/                  # API routes
│   └── components/               # React Components
│       ├── Avatar.tsx             # Simli animated avatar
│       ├── interview/
│       │   ├── MediaPipeOverlay.tsx
│       │   └── TelemetryPopup.tsx
│       └── ui/                   # Design system
│
├── assets/                       # SVG assets
├── tests/                        # Test suite
├── scripts/                      # Dev utilities
└── uploads/                      # Resume & report storage
```

<img width="100%" src="assets/divider.svg" alt="divider"/>

## `// quickstart`

### Prerequisites

```bash
$ cat /etc/aegis/requirements

PYTHON       =  3.11+
NODE         =  18+
UV           =  curl -LsSf https://astral.sh/uv/install.sh | sh
TESSERACT    =  brew install tesseract  # macOS (optional, for OCR)
```

### API Keys Required

```bash
$ cat .env.example

LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
GROQ_API_KEY=gsk_your_groq_key
DEEPGRAM_API_KEY=your_deepgram_key
SIMLI_API_KEY=your_simli_key           # Optional: Avatar
SIMLI_FACE_ID=your_face_id             # Optional: Avatar
```

### Installation

```bash
# Clone
git clone https://github.com/your-org/aegis-forge.git && cd aegis-forge

# Backend (Python)
uv sync --all-extras --dev

# Frontend (Node)
cd frontend && npm install && cd ..
```

### Running (3 Terminals)

```bash
# Terminal 1: Backend API
uvicorn backend.main:app --reload --port 8000

# Terminal 2: LiveKit Agent
python -m livekit.agents dev app.main:server

# Terminal 3: Frontend
cd frontend && npm run dev
```

Open **http://localhost:3000** and upload a resume to begin.

<img width="100%" src="assets/divider.svg" alt="divider"/>

## `// interview_domains`

| Domain | Scenario | Crisis Example |
| :-- | :--: | :-- |
| **AI/ML** | Model Drift | "Production model accuracy dropped 40% overnight" |
| **DevOps** | Redis Latency | "Redis cluster latency jumped from 2ms to 500ms" |
| **Cybersecurity** | Security Breach | "Unusual outbound traffic from payment gateway" |
| **Blockchain** | Smart Contract Exploit | "Re-entrancy attack draining contract funds" |
| **Backend** | API Outage | "Critical API returning 500s, customers affected" |
| **Frontend** | UI Crash | "Production React app crashing on render" |

<img width="100%" src="assets/divider.svg" alt="divider"/>

## `// performance`

| Metric | Value | Source |
| :-- | :--: | :-- |
| **Total Round-Trip** | **~850ms** | STT + LLM + TTS |
| **LLM Inference** | **~200ms** | Groq (Llama 3.1-8b) |
| **STT Latency** | **~150ms** | Deepgram Nova-3 |
| **TTS Latency** | **~200ms** | Deepgram Aura Asteria |
| **Interview Max** | **40 min** | Configurable timer |
| **5-min Warning** | **35 min** | Auto TTS warning |
| **Endpointing Delay** | **0.8s** | Tuned for noisy environments |

<img width="100%" src="assets/divider.svg" alt="divider"/>

## `// team`

<div align="center">

### Code Hashiras

| | Name | Role | GitHub |
| :-- | :-- | :-- | :-- |
| 🛡️ | **Utkarsh Singh** | Lead Engineer · Multi-Agent Architecture | [![GitHub](https://img.shields.io/badge/GitHub-D97706?style=flat-square&logo=github&logoColor=white&labelColor=151515)](https://github.com/utkarshsingh) |
| ⚔️ | **Ankit Choubey** | AI/ML Engineer · Agentic Systems | [![GitHub](https://img.shields.io/badge/GitHub-991B1B?style=flat-square&logo=github&logoColor=white&labelColor=151515)](https://github.com/ankit-choubey) |
| 🔧 | **Devraj Sahani** | Backend Engineer · API Infrastructure | [![GitHub](https://img.shields.io/badge/GitHub-FBBF24?style=flat-square&logo=github&logoColor=white&labelColor=151515)](https://github.com/devraj-sahani) |
| 🎨 | **Sankalp Tiwari** | Frontend Engineer · UI/UX | [![GitHub](https://img.shields.io/badge/GitHub-D97706?style=flat-square&logo=github&logoColor=white&labelColor=151515)](https://github.com/sankalp-tiwari) |

<br/>

**1st Runner-Up · Zenith National Hackathon · $1,500 Prize**

</div>

<img width="100%" src="assets/divider.svg" alt="divider"/>

## `// license`

```
Proprietary License · © 2026 FinalRound AI
All rights reserved. No license is granted.
See license.md for full terms.
```

<img width="100%" src="assets/footer.svg" alt="Aegis Forge Footer" />
