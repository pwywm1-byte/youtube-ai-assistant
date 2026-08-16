# 🎥 YouTube AI Assistant

An autonomous AI-powered system that generates YouTube content (Shorts and long-form videos) using a 14-agent pipeline backed by OpenAI, ElevenLabs, and the YouTube Data API v3.

## ✨ Features

### 🤖 14 Specialized AI Agents

| Agent | Role |
|---|---|
| TrendResearchAgent | Surfaces trending topics via OpenAI research |
| TopicSelectionAgent | Generates content plan and scores topics |
| ResearchAgent | Deep research brief for a given topic |
| ScriptwritingAgent | Full script (hook, intro, content, CTA, outro) |
| FactCheckingAgent | Verifies script claims |
| VoiceGenerationAgent | ElevenLabs TTS voiceover |
| VisualGenerationAgent | B-roll / scene descriptions |
| VideoEditingAgent | Video composition metadata |
| ThumbnailAgent | CTR-optimised thumbnail concepts & title suggestions |
| SEOAgent | Title, description, tags, keywords via OpenAI |
| QualityControlAgent | Pre-publish checklist |
| YouTubeUploadAgent | Uploads video to YouTube via Data API v3 |
| AnalyticsAgent | Fetches view/like/comment stats |
| OptimizationAgent | Growth recommendations from analytics |

### 🎬 Content Types
- **YouTube Shorts** (30–60 s)
- **Long-form Videos** (~15–20 min)
- **Daily batch** (1 Short + 1 Long-form)

### 🔗 Integrations
- YouTube Data API v3 (upload, stats)
- OpenAI GPT-4 (script, SEO, research, fact-check)
- ElevenLabs TTS (voiceover)
- FastAPI REST API

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- API keys (see [Environment Variables](#environment-variables))

### Installation

```bash
git clone https://github.com/pwywm1-byte/youtube-ai-assistant.git
cd youtube-ai-assistant

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
cp env.example .env              # edit .env with your API keys
```

### Run the API

```bash
uvicorn api.main:app --reload
# API docs at http://localhost:8000/docs
```

### Generate content

```bash
# Short-form video
curl -X POST http://localhost:8000/api/v1/content/generate-short

# Long-form video
curl -X POST http://localhost:8000/api/v1/content/generate-long

# Daily batch (1 Short + 1 Long)
curl -X POST http://localhost:8000/api/v1/content/generate-daily
```

---

## 🔑 Environment Variables

Copy `env.example` to `.env` and fill in the values.

### Required for AI generation

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | OpenAI API key — powers script, SEO, research, titles |
| `ELEVENLABS_API_KEY` | ElevenLabs key — voiceover generation |
| `ELEVENLABS_VOICE_ID` | Voice ID (default: Rachel `21m00Tcm4TlvDq8ikWAM`) |

### Required for YouTube publishing

| Variable | How to obtain |
|---|---|
| `YOUTUBE_CLIENT_ID` | Google Cloud Console → OAuth 2.0 Client ID |
| `YOUTUBE_CLIENT_SECRET` | Same OAuth client |
| `YOUTUBE_REFRESH_TOKEN` | Run `python -c "from services.youtube_service import YouTubeService; YouTubeService().run_oauth_flow()"` |
| `YOUTUBE_CHANNEL_ID` | Your channel ID (for analytics listing) |

> **Without credentials:** All agents fall back to mock/template data so the full pipeline runs without any keys. This is the default for local development.

### Optional

| Variable | Description |
|---|---|
| `OPENAI_MODEL` | Model name (default: `gpt-4`) |
| `DATABASE_URL` | PostgreSQL URL (not required to run the API) |
| `REDIS_URL` | Redis URL (for Celery task queue) |

---

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=. --cov-report=term-missing
```

Tests cover: API endpoints, all 14 agents (mock mode), workflow orchestrator, config loading, and database models.

---

## 🔍 Linting

```bash
black --line-length 100 .
flake8 --max-line-length 100 --extend-ignore E203,W503 .
```

---

## ⚙️ CI

GitHub Actions runs on every push/PR:
- **Lint job**: Black + Flake8
- **Test job**: Full pytest suite (no real credentials needed — agents run in mock mode)

See `.github/workflows/ci.yml`.

---

## 🏗️ Architecture

```
youtube-ai-assistant/
├── agents/          # 14 autonomous agents
├── api/             # FastAPI REST API
├── config/          # Settings (pydantic-settings)
├── models/          # SQLAlchemy ORM models
├── services/        # External API clients (OpenAI, YouTube, ElevenLabs)
├── tasks/           # Scheduled/background tasks
├── tests/           # pytest test suite
├── utils/           # Helpers
└── workflow/        # Orchestrator (coordinates agents end-to-end)
```

### Data flow (short-form example)

```
TrendResearch → TopicSelection → Research → Scriptwriting
    → FactChecking → VoiceGeneration → VisualGeneration
    → VideoEditing → Thumbnail → SEO → QualityControl
    → (optional) YouTubeUpload
```

---

## 🎬 YouTube Authentication

1. Create a project in [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **YouTube Data API v3**.
3. Create **OAuth 2.0 credentials** (Desktop app). Download `client_secrets.json` to the project root.
4. Run the OAuth flow once:

```python
from services.youtube_service import YouTubeService
YouTubeService().run_oauth_flow()
```

This saves a `youtube_token.json`. For production, use the `YOUTUBE_REFRESH_TOKEN` env var instead.

---

## 🐳 Docker

```bash
docker-compose up
```

---

## ⚠️ Known Limitations

- **Video encoding**: `VideoEditingAgent` describes the composition but does not render a real `.mp4` — actual encoding requires `ffmpeg` and the `moviepy` library wired to your asset pipeline.
- **Real thumbnails**: `ThumbnailAgent` generates title/concept suggestions; actual image creation requires a design API or PIL rendering pipeline.
- **Real trend data**: `TrendResearchAgent` uses OpenAI to surface likely trends; integration with Google Trends, Reddit, or YouTube Trending APIs is not yet wired.
- **Database**: SQLAlchemy models exist but no migration/seed scripts are included.
