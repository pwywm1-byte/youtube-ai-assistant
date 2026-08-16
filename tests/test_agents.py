"""Test agents module."""

import pytest
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


@pytest.mark.asyncio
async def test_trend_research_agent():
    """Test TrendResearchAgent."""
    agent = TrendResearchAgent()
    result = await agent.execute()
    assert result["success"] is True
    assert "trends" in result


@pytest.mark.asyncio
async def test_topic_selection_agent():
    """Test TopicSelectionAgent."""
    agent = TopicSelectionAgent()
    result = await agent.execute()
    assert result["success"] is True
    assert "selected_topics" in result


@pytest.mark.asyncio
async def test_research_agent():
    """Test ResearchAgent."""
    agent = ResearchAgent()
    result = await agent.execute(topic="AI")
    assert result["success"] is True
    assert "research" in result


@pytest.mark.asyncio
async def test_scriptwriting_agent():
    """Test ScriptwritingAgent."""
    agent = ScriptwritingAgent()
    result = await agent.execute(topic="AI", video_type="short")
    assert result["success"] is True
    assert "script" in result


@pytest.mark.asyncio
async def test_fact_checking_agent():
    """Test FactCheckingAgent."""
    agent = FactCheckingAgent()
    script = {"content": "AI is transforming the world. It has many use cases."}
    result = await agent.execute(script=script)
    assert result["success"] is True


@pytest.mark.asyncio
async def test_voice_generation_agent():
    """Test VoiceGenerationAgent."""
    agent = VoiceGenerationAgent()
    script = {"hook": "Hello!", "content": "Today we talk about AI.", "outro": "Bye!"}
    result = await agent.execute(script=script)
    assert result["success"] is True
    assert "audio" in result


@pytest.mark.asyncio
async def test_visual_generation_agent():
    """Test VisualGenerationAgent."""
    agent = VisualGenerationAgent()
    result = await agent.execute(topic="AI")
    assert result["success"] is True
    assert "visuals" in result


@pytest.mark.asyncio
async def test_video_editing_agent():
    """Test VideoEditingAgent."""
    agent = VideoEditingAgent()
    result = await agent.execute(video_type="short")
    assert result["success"] is True
    assert "video" in result


@pytest.mark.asyncio
async def test_thumbnail_agent():
    """Test ThumbnailAgent."""
    agent = ThumbnailAgent()
    result = await agent.execute(topic="AI")
    assert result["success"] is True
    assert "thumbnail" in result


@pytest.mark.asyncio
async def test_seo_agent():
    """Test SEOAgent."""
    agent = SEOAgent()
    result = await agent.execute(topic="AI")
    assert result["success"] is True
    assert "metadata" in result


@pytest.mark.asyncio
async def test_quality_control_agent():
    """Test QualityControlAgent."""
    agent = QualityControlAgent()
    video = {"file_path": "video.mp4", "duration": 60}
    metadata = {"title": "Test", "description": "Desc"}
    result = await agent.execute(video=video, metadata=metadata)
    assert result["success"] is True
    assert "ready_to_publish" in result


@pytest.mark.asyncio
async def test_youtube_upload_agent_no_path():
    """Test YouTubeUploadAgent returns error without video_path."""
    agent = YouTubeUploadAgent()
    result = await agent.execute(metadata={"title": "Test", "description": "Desc"})
    assert result["success"] is False


@pytest.mark.asyncio
async def test_analytics_agent():
    """Test AnalyticsAgent without video_id."""
    agent = AnalyticsAgent()
    result = await agent.execute()
    assert result["success"] is True
    assert "analytics" in result


@pytest.mark.asyncio
async def test_optimization_agent():
    """Test OptimizationAgent."""
    agent = OptimizationAgent()
    result = await agent.execute(analytics={"views": 100, "likes": 10})
    assert result["success"] is True
    assert "recommendations" in result
