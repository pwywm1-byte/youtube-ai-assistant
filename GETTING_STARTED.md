# 🎬 YouTube AI Assistant

**Fully autonomous AI-powered YouTube content generation system**

Generate, optimize, and publish professional YouTube videos automatically with AI.

## ✨ Features

- 🤖 **15 Autonomous Agents** - Each specialized for different tasks
- 📹 **Dual Format** - YouTube Shorts (30-60s) + Long-form (15-25min)
- 🔍 **Trend Research** - Analyzes YouTube, Google, Reddit, News
- ✍️ **Script Writing** - Original, engaging content with hooks
- 🎙️ **Voice Generation** - Professional AI voiceovers (ElevenLabs)
- 🎨 **Visual Generation** - AI graphics + stock footage + animations
- ✅ **Fact Checking** - Automatic claim verification
- 📊 **SEO Optimization** - Smart titles, descriptions, tags
- 📤 **YouTube Publishing** - Automatic upload with scheduling
- 📈 **Analytics Tracking** - Views, engagement, retention metrics
- 🎯 **Continuous Learning** - Optimizes based on performance

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- API Keys: OpenAI, Anthropic, ElevenLabs, YouTube

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
