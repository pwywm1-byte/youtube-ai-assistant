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
