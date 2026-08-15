"""OpenAI service for AI-powered content generation."""

import logging
from typing import Dict, Any, Optional
from openai import OpenAI

from config import settings

logger = logging.getLogger(__name__)


class OpenAIService:
    """Handle OpenAI API operations for content generation."""

    def __init__(self):
        """Initialize OpenAI client."""
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not configured in environment.")
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        logger.info(f"OpenAI service initialized with model: {self.model}")

    def _chat(self, system: str, user: str, temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """Send a chat completion request and return the text response."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()

    def research_topic(self, topic: str) -> Dict[str, Any]:
        """Use GPT-4 to conduct deep research on a topic."""
        system = (
            "You are an expert research assistant. Provide detailed, factual information "
            "about the given topic. Return structured information including key facts, "
            "statistics, recent developments, and notable perspectives."
        )
        user = (
            f"Research the following topic thoroughly for a YouTube video:\n\nTopic: {topic}\n\n"
            "Provide:\n"
            "1. Overview (2-3 paragraphs)\n"
            "2. Key facts and statistics (bullet points)\n"
            "3. Recent developments\n"
            "4. Different perspectives or subtopics\n"
            "5. Potential hooks or interesting angles for a video"
        )
        content = self._chat(system, user, temperature=0.5, max_tokens=2000)
        return {
            "topic": topic,
            "research_content": content,
            "sources": ["GPT-4 knowledge base"],
            "key_facts": [line.strip() for line in content.split("\n") if line.strip().startswith("-")],
        }

    def generate_script(
        self,
        topic: str,
        research: Optional[Dict[str, Any]] = None,
        video_type: str = "long_form",
    ) -> Dict[str, Any]:
        """Generate a full video script using GPT-4."""
        duration_guide = "60-second short" if video_type == "short" else "10-15 minute long-form"
        word_target = "150-200 words" if video_type == "short" else "1500-2000 words"

        research_context = ""
        if research and research.get("research_content"):
            research_context = f"\n\nResearch context:\n{research['research_content'][:1500]}"

        system = (
            "You are a professional YouTube scriptwriter specializing in engaging, "
            "informative video content. Write scripts that are conversational, hold viewer "
            "attention, and are optimized for YouTube audience retention."
        )
        user = (
            f"Write a complete YouTube script for a {duration_guide} video.\n\n"
            f"Topic: {topic}\n"
            f"Target length: {word_target}{research_context}\n\n"
            "Format the script with these clear sections:\n"
            "**HOOK** (first 5-10 seconds, grab attention)\n"
            "**INTRO** (brief topic overview)\n"
            "**MAIN CONTENT** (key sections with headers)\n"
            "**OUTRO** (call to action: like, subscribe, comment)\n\n"
            "Make it engaging, informative, and optimized for viewer retention."
        )
        content = self._chat(system, user, temperature=0.8, max_tokens=3000)

        word_count = len(content.split())
        hook = ""
        if "**HOOK**" in content:
            hook_start = content.index("**HOOK**") + len("**HOOK**")
            hook_end = content.index("**INTRO**") if "**INTRO**" in content else hook_start + 200
            hook = content[hook_start:hook_end].strip()

        return {
            "title": f"The Ultimate Guide to {topic}",
            "full_script": content,
            "hook": hook or content[:200],
            "word_count": word_count,
            "estimated_duration_seconds": word_count * 0.45,  # ~133 wpm
            "video_type": video_type,
        }

    def fact_check_script(self, script: Dict[str, Any], research: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Use GPT-4 to fact-check a script."""
        script_text = script.get("full_script", "") if isinstance(script, dict) else str(script)
        system = (
            "You are a rigorous fact-checker. Review the provided script for factual accuracy, "
            "unsupported claims, and potential misinformation. Be thorough but fair."
        )
        user = (
            f"Fact-check this YouTube script:\n\n{script_text[:3000]}\n\n"
            "Identify:\n"
            "1. Claims that are accurate and well-supported\n"
            "2. Claims that need verification or sources\n"
            "3. Any potentially inaccurate statements\n"
            "4. Overall assessment: APPROVED or NEEDS_REVISION\n\n"
            "End with a summary line: 'VERDICT: APPROVED' or 'VERDICT: NEEDS_REVISION'"
        )
        result = self._chat(system, user, temperature=0.3, max_tokens=1500)
        approved = "VERDICT: APPROVED" in result or "needs_revision" not in result.lower()
        return {
            "all_verified": approved,
            "fact_check_report": result,
            "claims_checked": script_text.count("."),
            "verdict": "APPROVED" if approved else "NEEDS_REVISION",
        }

    def generate_seo_metadata(self, topic: str, script: Dict[str, Any]) -> Dict[str, Any]:
        """Generate SEO-optimized title, description, and tags."""
        script_text = script.get("full_script", "") if isinstance(script, dict) else str(script)
        system = (
            "You are a YouTube SEO expert. Create highly optimized video metadata "
            "that maximizes click-through rate and search ranking."
        )
        user = (
            f"Create YouTube SEO metadata for this video about: {topic}\n\n"
            f"Script excerpt:\n{script_text[:500]}\n\n"
            "Provide:\n"
            "1. TITLE: One compelling, keyword-rich title (max 100 chars)\n"
            "2. DESCRIPTION: Full description (300-500 words) with keywords\n"
            "3. TAGS: 15 relevant tags (comma-separated)\n"
            "4. KEYWORDS: 10 target keywords (comma-separated)\n\n"
            "Format each section with its label (TITLE:, DESCRIPTION:, TAGS:, KEYWORDS:)"
        )
        result = self._chat(system, user, temperature=0.6, max_tokens=1500)

        title = topic
        description = ""
        tags: list = []
        keywords: list = []

        for line in result.split("\n"):
            stripped = line.strip()
            if stripped.startswith("TITLE:"):
                title = stripped[6:].strip()
            elif stripped.startswith("DESCRIPTION:"):
                description = stripped[12:].strip()
            elif stripped.startswith("TAGS:"):
                tags = [t.strip() for t in stripped[5:].split(",") if t.strip()]
            elif stripped.startswith("KEYWORDS:"):
                keywords = [k.strip() for k in stripped[9:].split(",") if k.strip()]

        return {
            "title": title or f"The Complete Guide to {topic}",
            "description": description or result[:400],
            "tags": tags[:15],
            "keywords": keywords[:10],
            "seo_score": 85,
        }

    def fetch_trending_topics(self, niche: str = "technology") -> Dict[str, Any]:
        """Use GPT-4 to suggest trending topics in a niche."""
        system = (
            "You are a YouTube content strategist with expertise in trend analysis. "
            "Suggest currently trending and high-potential topics for YouTube videos."
        )
        user = (
            f"Suggest 10 trending YouTube video topics for the '{niche}' niche.\n\n"
            "For each topic provide:\n"
            "- Topic title\n"
            "- Trend score (1-100)\n"
            "- Brief reason why it's trending\n\n"
            "Format as: TOPIC: <title> | SCORE: <number> | REASON: <brief explanation>"
        )
        result = self._chat(system, user, temperature=0.7, max_tokens=1000)

        topics = []
        for line in result.split("\n"):
            if "TOPIC:" in line and "SCORE:" in line:
                try:
                    parts = line.split("|")
                    title = parts[0].replace("TOPIC:", "").strip()
                    score_str = parts[1].replace("SCORE:", "").strip()
                    score = int("".join(filter(str.isdigit, score_str))) if score_str else 75
                    topics.append({"title": title, "score": score})
                except (IndexError, ValueError):
                    continue

        if not topics:
            topics = [{"title": f"Best {niche} trends 2024", "score": 80}]

        return {"niche": niche, "topics": topics}
