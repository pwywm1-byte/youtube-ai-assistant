"""Content orchestrator that coordinates all agents."""

import logging
import asyncio
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
)

logger = logging.getLogger(__name__)


class ContentOrchestrator:
    """Orchestrate complete content generation workflow."""

    def __init__(self):
        """Initialize orchestrator with all agents."""
        self.trend_agent = TrendResearchAgent()
        self.topic_agent = TopicSelectionAgent()
        self.research_agent = ResearchAgent()
        self.script_agent = ScriptwritingAgent()
        self.fact_check_agent = FactCheckingAgent()
        self.voice_agent = VoiceGenerationAgent()
        self.visual_agent = VisualGenerationAgent()
        self.video_agent = VideoEditingAgent()
        self.thumbnail_agent = ThumbnailAgent()
        self.seo_agent = SEOAgent()
        self.quality_agent = QualityControlAgent()
        self.upload_agent = YouTubeUploadAgent()
        self.analytics_agent = AnalyticsAgent()

    async def generate_complete_video(self, video_type: str = "both") -> Dict[str, Any]:
        """Generate complete video from research to upload.

        Args:
            video_type: 'short', 'long_form', or 'both'

        Returns:
            Complete video generation result
        """
        logger.info(f"Starting content generation pipeline ({video_type})...")

        try:
            # Step 1: Research trends
            logger.info("Step 1: Researching trends...")
            trends = await self.trend_agent.execute()

            # Step 2: Select best topic
            logger.info("Step 2: Selecting topic...")
            topic_result = await self.topic_agent.execute(trends=trends)
            selected_topic = topic_result["selected_topics"][0]

            # Step 3: Deep research
            logger.info("Step 3: Researching topic...")
            research = await self.research_agent.execute(topic=selected_topic["title"])

            # Step 4: Write script
            logger.info("Step 4: Writing script...")
            script = await self.script_agent.execute(
                topic=selected_topic["title"],
                research=research,
                video_type=video_type,
            )

            # Step 5: Fact check
            logger.info("Step 5: Fact checking...")
            fact_check = await self.fact_check_agent.execute(
                script=script, research=research
            )

            if not fact_check["all_verified"]:
                logger.warning("Some facts could not be verified!")

            # Step 6: Generate voice
            logger.info("Step 6: Generating voiceover...")
            audio = await self.voice_agent.execute(script=script)

            # Step 7: Generate visuals
            logger.info("Step 7: Generating visuals...")
            visuals = await self.visual_agent.execute(
                script=script, topic=selected_topic["title"], video_type=video_type
            )

            # Step 8: Edit video
            logger.info("Step 8: Editing video...")
            video = await self.video_agent.execute(
                visuals=visuals, audio=audio, script=script
            )

            # Step 9: Generate thumbnail
            logger.info("Step 9: Generating thumbnail...")
            thumbnail = await self.thumbnail_agent.execute(
                topic=selected_topic["title"], script=script, visuals=visuals
            )

            # Step 10: Optimize SEO
            logger.info("Step 10: Optimizing SEO...")
            metadata = await self.seo_agent.execute(
                topic=selected_topic["title"], script=script, research=research
            )

            # Step 11: Quality control
            logger.info("Step 11: Running quality control...")
            quality_result = await self.quality_agent.execute(
                video=video, metadata=metadata
            )

            if not quality_result["ready_to_publish"]:
                logger.error("Video failed quality control!")
                return {"success": False, "error": "Quality control failed"}

            # Step 12: Upload to YouTube
            logger.info("Step 12: Uploading to YouTube...")
            upload_result = await self.upload_agent.execute(
                video_path=video["file_path"],
                metadata=metadata,
                thumbnail_path=thumbnail["file_path"],
            )

            logger.info(f"✅ Video generation complete! Video ID: {upload_result['video_id']}")

            return {
                "success": True,
                "topic": selected_topic,
                "video": video,
                "metadata": metadata,
                "thumbnail": thumbnail,
                "upload_result": upload_result,
            }

        except Exception as e:
            logger.error(f"❌ Error in content generation: {str(e)}")
            return {"success": False, "error": str(e)}

    async def generate_daily_content(self):
        """Generate 1 Short + 1 Long-form video daily."""
        logger.info("🎬 Starting daily content generation...")

        try:
            # Generate Short
            logger.info("Generating YouTube Short...")
            short_result = await self.generate_complete_video(video_type="short")

            # Generate Long-form
            logger.info("Generating Long-form video...")
            longform_result = await self.generate_complete_video(video_type="long_form")

            return {
                "success": all([short_result["success"], longform_result["success"]]),
                "short": short_result,
                "long_form": longform_result,
            }

        except Exception as e:
            logger.error(f"Error in daily content generation: {str(e)}")
            return {"success": False, "error": str(e)}
