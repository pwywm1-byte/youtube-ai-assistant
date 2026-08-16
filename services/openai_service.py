"""OpenAI integration service for content generation."""

import json
import logging
import time
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI, APIError, RateLimitError, APITimeoutError

logger = logging.getLogger(__name__)

_RETRY_ERRORS = (RateLimitError, APITimeoutError)
_MAX_RETRIES = 3
_RETRY_DELAY = 2  # seconds


def _mock_script(topic: str, word_count: int) -> Dict[str, Any]:
    return {
        "title": f"Top Tips About {topic}",
        "hook": f"Hey everyone, today we're diving into {topic}...",
        "intro": f"Welcome back! Today's topic is {topic}.",
        "content": f"Here is the main content about {topic}. "
        "We will cover key aspects, recent developments, "
        "and actionable insights.",
        "cta": "If you found this helpful, smash that like button and subscribe!",
        "outro": "Thanks for watching — see you in the next video!",
        "word_count": word_count,
    }


def _mock_metadata(topic: str) -> Dict[str, Any]:
    words = topic.lower().split()
    tags = list({topic.lower(), *words, "youtube", "tutorial", "tips", "howto"})
    return {
        "title": f"{topic}: Everything You Need to Know in 2024",
        "description": (
            f"In this video we explore {topic} in depth. "
            "Whether you're a beginner or advanced, this guide covers "
            "key concepts, practical tips, and real-world examples.\n\n"
            f"🔑 Topics covered:\n• What is {topic}?\n"
            "• Key benefits and use-cases\n"
            "• Step-by-step walkthrough\n"
            "• Common mistakes to avoid\n\n"
            "👍 Like, comment, and subscribe for more content like this!"
        ),
        "tags": tags[:15],
        "keywords": words[:10],
        "seo_score": 75,
    }


class OpenAIService:
    """Handle OpenAI API operations for content generation."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """Initialize OpenAI service."""
        self.api_key = api_key
        self.model = model
        self._client: Optional[AsyncOpenAI] = None
        if api_key:
            self._client = AsyncOpenAI(api_key=api_key)
        logger.info("OpenAI Service initialized with model: %s", model)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Call ChatCompletion with basic retry logic."""
        if not self._client:
            raise RuntimeError("OpenAI client not initialised (no API key)")
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                response = await self._client.chat.completions.create(
                    model=self.model,
                    messages=messages,  # type: ignore[arg-type]
                    **kwargs,
                )
                return response.choices[0].message.content or ""
            except _RETRY_ERRORS as exc:
                if attempt == _MAX_RETRIES:
                    raise
                wait = _RETRY_DELAY * attempt
                logger.warning(
                    "OpenAI rate/timeout error (attempt %d/%d): %s — retrying in %ds",
                    attempt,
                    _MAX_RETRIES,
                    exc,
                    wait,
                )
                time.sleep(wait)
            except APIError as exc:
                logger.error("OpenAI API error: %s", exc)
                raise

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def generate_script(
        self,
        topic: str,
        research: Optional[Dict[str, Any]] = None,
        video_type: str = "long_form",
        word_count: int = 1500,
    ) -> Dict[str, Any]:
        """Generate a video script for *topic*.

        Falls back to a template when no API key is configured so the
        pipeline can run end-to-end without credentials during development.
        """
        if not self._client:
            logger.warning("OpenAI API key not set — returning template script")
            return {"success": True, "script": _mock_script(topic, word_count), "used_mock": True}

        research_summary = ""
        if research and research.get("summary"):
            research_summary = f"\n\nResearch summary:\n{research['summary']}"

        duration_hint = "30–60 seconds" if video_type == "short" else "15–20 minutes"
        prompt = (
            "You are an expert YouTube scriptwriter. "
            f"Write a compelling {video_type.replace('_', ' ')} "
            f"YouTube video script about: {topic}.\n"
            f"Target duration: {duration_hint} (~{word_count} words).\n"
            f"{research_summary}\n\n"
            "Return ONLY valid JSON with these keys:\n"
            '{"title": "...", "hook": "...", "intro": "...", '
            '"content": "...", "cta": "...", "outro": "..."}'
        )
        try:
            raw = await self._chat(
                [{"role": "user", "content": prompt}],
                max_tokens=min(word_count * 2, 4000),
                temperature=0.7,
            )
            data = json.loads(raw)
            data.setdefault("word_count", len(data.get("content", "").split()))
            logger.info("Script generated for topic: %s", topic)
            return {"success": True, "script": data}
        except (json.JSONDecodeError, KeyError) as exc:
            logger.error("Failed to parse script JSON: %s", exc)
            return {"success": True, "script": _mock_script(topic, word_count), "used_mock": True}
        except Exception as exc:
            logger.error("Error generating script: %s", exc)
            return {"success": False, "error": str(exc)}

    async def generate_seo_metadata(
        self,
        topic: str,
        script: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate SEO-optimised title, description, tags and keywords."""
        if not self._client:
            logger.warning("OpenAI API key not set — returning template metadata")
            return {"success": True, "metadata": _mock_metadata(topic), "used_mock": True}

        script_excerpt = ""
        if script:
            script_excerpt = "\n\nScript excerpt:\n" + str(script.get("content", ""))[:800]

        prompt = (
            "You are a YouTube SEO specialist. "
            f"Generate optimised metadata for a video about: {topic}.\n"
            f"{script_excerpt}\n\n"
            "Return ONLY valid JSON with these keys:\n"
            '{"title": "...", "description": "...", "tags": [...],'
            ' "keywords": [...], "seo_score": 0-100}'
        )
        try:
            raw = await self._chat(
                [{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.5,
            )
            data = json.loads(raw)
            logger.info("SEO metadata generated for: %s", topic)
            return {"success": True, "metadata": data}
        except (json.JSONDecodeError, KeyError) as exc:
            logger.error("Failed to parse metadata JSON: %s", exc)
            return {"success": True, "metadata": _mock_metadata(topic), "used_mock": True}
        except Exception as exc:
            logger.error("Error generating SEO metadata: %s", exc)
            return {"success": False, "error": str(exc)}

    async def generate_titles(self, topic: str, count: int = 5) -> Dict[str, Any]:
        """Generate *count* YouTube title suggestions for *topic*."""
        if not self._client:
            titles = [
                f"{topic}: {suffix}"
                for suffix in [
                    "Complete Guide",
                    "You Won't Believe This",
                    "Everything Explained",
                    "Top 10 Tips",
                    "Beginner to Advanced",
                ][:count]
            ]
            return {"success": True, "titles": titles, "used_mock": True}

        prompt = (
            f"Generate {count} compelling YouTube video titles for the topic: {topic}.\n"
            "Make them click-worthy, specific, and SEO-friendly.\n"
            "Return ONLY a JSON array of strings."
        )
        try:
            raw = await self._chat([{"role": "user", "content": prompt}], max_tokens=300)
            titles = json.loads(raw)
            return {"success": True, "titles": titles}
        except Exception as exc:
            logger.error("Error generating titles: %s", exc)
            return {"success": False, "error": str(exc)}

    async def generate_hook(self, topic: str, video_type: str = "long_form") -> Dict[str, Any]:
        """Generate a compelling hook/intro for *topic*."""
        if not self._client:
            hook = (
                f"In the next {('60 seconds' if video_type == 'short' else '15 minutes')}, "
                f"I'm going to show you everything you need to know about {topic}. "
                "Stay until the end — there's a tip most people miss completely."
            )
            return {"success": True, "hook": hook, "used_mock": True}

        prompt = (
            "Write a compelling 2–3 sentence hook/intro for a "
            f"YouTube {'Short' if video_type == 'short' else 'video'} "
            f"about: {topic}.\n"
            "The hook should immediately grab attention and promise value. "
            "Return ONLY the hook text."
        )
        try:
            hook = await self._chat([{"role": "user", "content": prompt}], max_tokens=150)
            return {"success": True, "hook": hook.strip()}
        except Exception as exc:
            logger.error("Error generating hook: %s", exc)
            return {"success": False, "error": str(exc)}

    async def research_topic(self, topic: str) -> Dict[str, Any]:
        """Generate a structured research brief for *topic*."""
        if not self._client:
            return {
                "success": True,
                "research": {
                    "topic": topic,
                    "summary": f"Overview of {topic} with key facts and recent developments.",
                    "key_points": [
                        f"Key fact 1 about {topic}",
                        f"Key fact 2 about {topic}",
                        f"Key fact 3 about {topic}",
                    ],
                    "sources": [],
                    "audience": "General audience interested in " + topic,
                },
                "used_mock": True,
            }

        prompt = (
            f"Research the following topic for a YouTube video: {topic}.\n"
            "Provide a structured research brief. Return ONLY valid JSON with:\n"
            '{"summary": "...", "key_points": [...], "audience": "...", "angle": "..."}'
        )
        try:
            raw = await self._chat([{"role": "user", "content": prompt}], max_tokens=800)
            data = json.loads(raw)
            data["topic"] = topic
            data.setdefault("sources", [])
            return {"success": True, "research": data}
        except (json.JSONDecodeError, KeyError) as exc:
            logger.error("Failed to parse research JSON: %s", exc)
            return {"success": False, "error": str(exc)}
        except Exception as exc:
            logger.error("Error researching topic: %s", exc)
            return {"success": False, "error": str(exc)}

    async def fact_check(
        self,
        claims: List[str],
        research: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Fact-check a list of claims against research context."""
        if not self._client:
            logger.warning("OpenAI API key not set — skipping fact-check")
            return {
                "success": True,
                "results": {
                    "claims_checked": len(claims),
                    "verified": len(claims),
                    "unverified": 0,
                    "details": [{"claim": c, "status": "unverified"} for c in claims],
                },
                "used_mock": True,
            }

        context = ""
        if research:
            context = "\nContext:\n" + str(research.get("summary", ""))[:600]

        claims_text = "\n".join(f"- {c}" for c in claims)
        prompt = (
            f"Fact-check the following claims:{context}\n\nClaims:\n{claims_text}\n\n"
            "Return ONLY valid JSON:\n"
            '{"details": [{"claim": "...", "status": "verified|unverified|false", "note": "..."}]}'
        )
        try:
            raw = await self._chat([{"role": "user", "content": prompt}], max_tokens=600)
            data = json.loads(raw)
            details = data.get("details", [])
            verified = sum(1 for d in details if d.get("status") == "verified")
            return {
                "success": True,
                "results": {
                    "claims_checked": len(details),
                    "verified": verified,
                    "unverified": len(details) - verified,
                    "details": details,
                },
            }
        except Exception as exc:
            logger.error("Error fact-checking: %s", exc)
            return {"success": False, "error": str(exc)}

    async def generate_content_plan(self, niche: str, weeks: int = 4) -> Dict[str, Any]:
        """Generate a content plan for *niche* covering *weeks* of videos."""
        if not self._client:
            plan = []
            for week in range(1, weeks + 1):
                plan.append(
                    {
                        "week": week,
                        "short": {"topic": f"{niche} tip #{week}", "type": "short"},
                        "long": {
                            "topic": f"Deep dive into {niche} — part {week}",
                            "type": "long_form",
                        },
                    }
                )
            return {"success": True, "plan": plan, "used_mock": True}

        prompt = (
            f"Create a {weeks}-week YouTube content plan for the niche: {niche}.\n"
            "For each week include one Short and one Long-form video idea.\n"
            'Return ONLY valid JSON: [{"week": 1, '
            '"short": {"topic": "...", "angle": "..."}, '
            '"long": {"topic": "...", "angle": "..."}}]'
        )
        try:
            raw = await self._chat([{"role": "user", "content": prompt}], max_tokens=1000)
            plan = json.loads(raw)
            return {"success": True, "plan": plan}
        except Exception as exc:
            logger.error("Error generating content plan: %s", exc)
            return {"success": False, "error": str(exc)}
