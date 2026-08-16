# 🎥 YouTube AI Assistant

An autonomous AI-powered system that generates high-quality YouTube videos (both shorts and long-form) completely hands-free using multi-agent orchestration.

## ✨ Features

### 🤖 14 Specialized AI Agents
- **TrendResearchAgent**: Identifies trending topics
- **TopicSelectionAgent**: Selects optimal topics
- **ResearchAgent**: Conducts deep research
- **ScriptwritingAgent**: Generates compelling scripts
- **FactCheckingAgent**: Verifies claims
- **VoiceGenerationAgent**: Creates voiceovers using ElevenLabs
- **VisualGenerationAgent**: Generates visuals
- **VideoEditingAgent**: Assembles video content
- **ThumbnailAgent**: Designs thumbnails
- **SEOAgent**: Optimizes metadata
- **QualityControlAgent**: Quality assurance
- **YouTubeUploadAgent**: Publishing automation
- **AnalyticsAgent**: Tracks performance
- **OptimizationAgent**: Improves based on analytics

### 🎬 Content Types
- **YouTube Shorts** (30-60s)
- **Long-form Videos** (15-25 min)
- **Daily Content** (1 Short + 1 Long)

### 🔗 Integrations
- YouTube API
- OpenAI GPT-4
- ElevenLabs TTS
- PostgreSQL
- Redis

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 13+
- Redis 6+
- API Keys (YouTube, OpenAI, ElevenLabs)

### Installation

```bash
# Clone repository
git clone https://github.com/pwywm1-byte/youtube-ai-assistant.git
cd youtube-ai-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your API keys
```

### Running

```bash
python -m api.main
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

## 📡 API Endpoints

```bash
GET /                              # Root
GET /health                        # Health check
GET /api/v1/status                # System status
GET /api/v1/agents                # List agents

POST /api/v1/content/generate-short     # Generate Short
POST /api/v1/content/generate-long      # Generate Long-form
POST /api/v1/content/generate-daily     # Generate Daily Content

GET /api/v1/task/{task_id}        # Task status
GET /api/v1/tasks                 # List tasks
```

## 🏗️ Architecture

```
Trend Research → Topic Selection → Research → Script Writing 
→ Fact Checking → Voice Generation → Visual Generation 
→ Video Editing → Thumbnail Design → SEO Optimization 
→ Quality Control → YouTube Upload → Analytics → Optimization
```

## 🧪 Testing

```bash
pytest tests/ -v
pytest tests/ --cov=.
```

## 📊 Database Models

- **Topic**: Trending topics
- **Script**: Generated scripts
- **Video**: Video files & metadata
- **Metadata**: SEO metadata
- **Analytics**: YouTube statistics
- **Credential**: API credentials

## 🔧 Configuration

See `.env.example` for all configuration options.

## 📈 Performance

- Short-form: ~2-3 minutes
- Long-form: ~5-10 minutes
- Daily (1 Short + 1 Long): ~15-20 minutes

## 🔐 Security

- Environment variables for secrets
- Encrypted database credentials
- Rate limiting
- CORS protection
- Input validation

## 📞 Support

- Issues: GitHub Issues
- Discussions: GitHub Discussions

## 📝 License

MIT License
