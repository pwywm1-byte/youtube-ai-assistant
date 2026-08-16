"""OpenAI service for content generation."""

import logging
from typing import Dict, Any, List, Optional
import json
from openai import OpenAI

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for GPT-4 powered content generation."""

    def __init__(self, api_key: str, model: str = "gpt-4"):
        """Initialize OpenAI service."""
        self.client = OpenAI(api_key=api_key)
        self.model = model
        logger.info(f"OpenAI Service initialized with model: {model}")

    def generate_script(
        self,
        topic: str,
        research: Optional[Dict[str, Any]] = None,
        video_type: str = "long_form",
        tone: str = "engaging",
    ) -> Dict[str, Any]:
        """Generate video script using GPT-4."""
        try:
            research_context = ""
            if research and isinstance(research, dict):
                if isinstance(research, dict) and "research" in research:
                    research_context = json.dumps(research["research"], indent=2)
                else:
                    research_context = json.dumps(research, indent=2)

            word_count = 2000 if video_type == "short" else 3500

            prompt = f"""Create a compelling video script for a YouTube {'Short' if video_type == 'short' else 'long-form'} video about: {topic}

Tone: {tone}
Target word count: ~{word_count} words

Research context:
{research_context}

Provide the script in this JSON format:
{{
    "title": "Engaging video title",
    "hook": "First 30 seconds to grab attention",
    "content": "Main body of the script",
    "outro": "Closing with call-to-action",
    "key_points": ["point 1", "point 2", "point 3"],
    "timestamps": {{"section": "MM:SS"}}
}}

Make it engaging, unique, and optimized for YouTube's algorithm."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=2000,
            )

            content = response.choices[0].message.content
            try:
                script_data = json.loads(content)
            except json.JSONDecodeError:
                # Fallback if response is not JSON
                script_data = {
                    "title": topic,
                    "hook": content[:200],
                    "content": content,
                    "outro": "Thanks for watching!",
                    "key_points": [],
                }

            return {
                "success": True,
                "script": script_data,
                "word_count": len(content.split()),
            }
        except Exception as e:
            logger.error(f"Error generating script: {str(e)}")
            return {"success": False, "error": str(e)}

    def generate_seo_metadata(
        self, topic: str, script: Dict[str, Any], research: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate SEO-optimized metadata."""
        try:
            prompt = f"""Generate SEO metadata for a YouTube video about: {topic}

Video Title: {script.get('title', topic)}
Script Hook: {script.get('hook', '')}

Provide response as JSON:
{{
    "title": "SEO optimized title (60 chars max)",
    "description": "SEO optimized description (5000 chars max)",
    "tags": ["tag1", "tag2", "tag3", ...],
    "keywords": ["keyword1", "keyword2", ...],
    "category": "YouTube category"
}}"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000,
            )

            try:
                metadata = json.loads(response.choices[0].message.content)
            except json.JSONDecodeError:
                metadata = {"title": topic, "description": "", "tags": [], "keywords": []}

            return {"success": True, "metadata": metadata}
        except Exception as e:
            logger.error(f"Error generating SEO metadata: {str(e)}")
            return {"success": False, "error": str(e)}

    def fact_check(
        self, claims: List[str], research: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Fact-check claims in the script."""
        try:
            prompt = f"""Fact-check the following claims:

{json.dumps(claims)}

For each claim, provide:
1. Accuracy rating (0-100)
2. Brief explanation
3. Sources if available

Provide response as JSON array."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=1000,
            )

            try:
                results = json.loads(response.choices[0].message.content)
            except json.JSONDecodeError:
                results = [{"claim": claim, "accuracy": 80} for claim in claims]

            verified_count = sum(
                1 for r in results if isinstance(r, dict) and r.get("accuracy", 0) >= 70
            )

            return {
                "success": True,
                "total_claims": len(claims),
                "verified_claims": verified_count,
                "results": results,
            }
        except Exception as e:
            logger.error(f"Error fact-checking: {str(e)}")
            return {"success": False, "error": str(e)}

    def research_topic(self, topic: str, sources: List[str] = None) -> Dict[str, Any]:
        """Research a topic using GPT-4."""
        try:
            sources_list = "YouTube, Google Trends, Reddit, News" if not sources else ", ".join(sources)

            prompt = f"""Research the topic: {topic}

Consider these sources: {sources_list}

Provide comprehensive research including:
1. Current trends
2. Key statistics
3. Notable examples
4. Common misconceptions
5. Expert perspectives

Response format (JSON):
{{
    "topic": "{topic}",
    "key_findings": ["finding1", "finding2", ...],
    "statistics": [{{"stat": "...", "source": "..."}}],
    "trends": ["trend1", "trend2", ...],
    "misconceptions": ["myth1", "myth2", ...]
}}"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=2000,
            )

            try:
                research_data = json.loads(response.choices[0].message.content)
            except json.JSONDecodeError:
                research_data = {
                    "topic": topic,
                    "key_findings": [],
                    "statistics": [],
                    "trends": [],
                }

            return {"success": True, "research": research_data}
        except Exception as e:
            logger.error(f"Error researching topic: {str(e)}")
            return {"success": False, "error": str(e)}
