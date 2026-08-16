"""Workflow orchestrator for content generation pipeline."""

import logging
from typing import Dict, Any
from agents import (
    TrendResearchAgent,
    TopicSelectionAgent,
    ResearchAgent,
    ScriptwritingAgent,
    FactCheckingAgent,
    VoiceGenerationAgent,
    VisualGenerationAgent,
    VideoEditingAgent,
    ThumbnailAgent,
    SEOAgent,
    QualityControlAgent,
    YouTubeUploadAgent,
    AnalyticsAgent,
    OptimizationAgent,
)

logger = logging.getLogger(__name__)


class ContentOrchestrator:
    """Orchestrates the entire content generation pipeline."""

    def __init__(self):
        """Initialize all agents."""
        self.trend_research = TrendResearchAgent()
        self.topic_selection = TopicSelectionAgent()
        self.research = ResearchAgent()
        self.scriptwriting = ScriptwritingAgent()
        self.fact_checking = FactCheckingAgent()
        self.voice_generation = VoiceGenerationAgent()
        self.visual_generation = VisualGenerationAgent()
        self.video_editing = VideoEditingAgent()
        self.thumbnail = ThumbnailAgent()
        self.seo = SEOAgent()
        self.quality_control = QualityControlAgent()
        self.youtube_upload = YouTubeUploadAgent()
        self.analytics = AnalyticsAgent()
        self.optimization = OptimizationAgent()

        logger.info("ContentOrchestrator initialized with 15 agents")

    async def generate_short_form(self, **kwargs) -> Dict[str, Any]:
        """Generate short-form video (YouTube Short 30-60s)."""
        logger.info("Starting short-form video generation...")

        try:
            trends_result = await self.trend_research.execute()
            if not trends_result.get("success"):
                return {"success": False, "error": "Trend research failed"}

            topic_result = await self.topic_selection.execute(trends=trends_result)
            if not topic_result.get("success"):
                return {"success": False, "error": "Topic selection failed"}

            selected_topic = topic_result.get("selected_topics", [{}])[0].get("title")

            research_result = await self.research.execute(topic=selected_topic)
            if not research_result.get("success"):
                return {"success": False, "error": "Research failed"}

            script_result = await self.scriptwriting.execute(
                topic=selected_topic,
                research=research_result,
                video_type="short",
            )
            if not script_result.get("success"):
                return {"success": False, "error": "Script writing failed"}

            script = script_result.get("script")

            await self.fact_checking.execute(script=script, research=research_result)
            voice_result = await self.voice_generation.execute(script=script)
            if not voice_result.get("success"):
                return {"success": False, "error": "Voice generation failed"}

            visuals_result = await self.visual_generation.execute(
                script=script,
                topic=selected_topic,
                video_type="short",
            )
            if not visuals_result.get("success"):
                return {"success": False, "error": "Visual generation failed"}

            video_result = await self.video_editing.execute(
                visuals=visuals_result.get("visuals"),
                audio=voice_result.get("audio"),
                script=script,
            )
            if not video_result.get("success"):
                return {"success": False, "error": "Video editing failed"}

            thumbnail_result = await self.thumbnail.execute(
                topic=selected_topic,
                script=script,
                visuals=visuals_result.get("visuals"),
            )

            seo_result = await self.seo.execute(
                topic=selected_topic,
                script=script,
                research=research_result,
            )

            qc_result = await self.quality_control.execute(
                video=video_result.get("video"),
                metadata=seo_result.get("metadata"),
            )
            if not qc_result.get("ready_to_publish"):
                return {"success": False, "error": "Quality control failed"}

            logger.info(f"✅ Short-form video generation complete for {selected_topic}")

            return {
                "success": True,
                "video_type": "short",
                "topic": selected_topic,
                "script": script,
                "video": video_result.get("video"),
                "thumbnail": thumbnail_result.get("thumbnail"),
                "metadata": seo_result.get("metadata"),
                "status": "ready_to_publish",
            }

        except Exception as e:
            logger.error(f"Error in short-form generation: {str(e)}")
            return {"success": False, "error": str(e)}

    async def generate_long_form(self, **kwargs) -> Dict[str, Any]:
        """Generate long-form video (15-25 minutes)."""
        logger.info("Starting long-form video generation...")

        try:
            trends_result = await self.trend_research.execute()
            topic_result = await self.topic_selection.execute(trends=trends_result)
            selected_topic = topic_result.get("selected_topics", [{}])[0].get("title")

            research_result = await self.research.execute(topic=selected_topic)
            script_result = await self.scriptwriting.execute(
                topic=selected_topic,
                research=research_result,
                video_type="long_form",
            )

            script = script_result.get("script")

            await self.fact_checking.execute(script=script, research=research_result)
            voice_result = await self.voice_generation.execute(script=script)
            visuals_result = await self.visual_generation.execute(
                script=script,
                topic=selected_topic,
                video_type="long_form",
            )
            video_result = await self.video_editing.execute(
                visuals=visuals_result.get("visuals"),
                audio=voice_result.get("audio"),
                script=script,
            )
            thumbnail_result = await self.thumbnail.execute(
                topic=selected_topic,
                script=script,
                visuals=visuals_result.get("visuals"),
            )
            seo_result = await self.seo.execute(
                topic=selected_topic,
                script=script,
                research=research_result,
            )
            qc_result = await self.quality_control.execute(
                video=video_result.get("video"),
                metadata=seo_result.get("metadata"),
            )

            logger.info(f"✅ Long-form video generation complete for {selected_topic}")

            return {
                "success": True,
                "video_type": "long_form",
                "topic": selected_topic,
                "script": script,
                "video": video_result.get("video"),
                "thumbnail": thumbnail_result.get("thumbnail"),
                "metadata": seo_result.get("metadata"),
                "status": "ready_to_publish",
            }

        except Exception as e:
            logger.error(f"Error in long-form generation: {str(e)}")
            return {"success": False, "error": str(e)}

    async def generate_daily_content(self, **kwargs) -> Dict[str, Any]:
        """Generate daily content: 1 short + 1 long-form."""
        logger.info("Starting daily content generation (1 Short + 1 Long-form)...")

        try:
            short_result = await self.generate_short_form()
            long_result = await self.generate_long_form()

            if short_result.get("success") and long_result.get("success"):
                logger.info("✅ Daily content generation successful!")
                return {
                    "success": True,
                    "short_form": short_result,
                    "long_form": long_result,
                }
            else:
                return {
                    "success": False,
                    "error": "One or more videos failed to generate",
                    "short_form": short_result,
                    "long_form": long_result,
                }

        except Exception as e:
            logger.error(f"Error in daily content generation: {str(e)}")
            return {"success": False, "error": str(e)}
