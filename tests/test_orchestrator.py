"""Tests for content orchestration."""

import pytest
import asyncio
from workflow.orchestrator import ContentOrchestrator


@pytest.fixture
def orchestrator():
    """Create orchestrator instance."""
    return ContentOrchestrator()


@pytest.mark.asyncio
async def test_trend_research(orchestrator):
    """Test trend research agent."""
    result = await orchestrator.trend_agent.execute()
    assert result["success"]
    assert "trends" in result


@pytest.mark.asyncio
async def test_topic_selection(orchestrator):
    """Test topic selection agent."""
    result = await orchestrator.topic_agent.execute()
    assert result["success"]
    assert "selected_topics" in result
    assert len(result["selected_topics"]) > 0


@pytest.mark.asyncio
async def test_research(orchestrator):
    """Test research agent."""
    result = await orchestrator.research_agent.execute(topic="AI")
    assert result["success"]
    assert "research" in result


@pytest.mark.asyncio
async def test_scriptwriting(orchestrator):
    """Test script writing agent."""
    result = await orchestrator.script_agent.execute(
        topic="AI",
        video_type="long_form"
    )
    assert result["success"]
    assert "script" in result
    assert "title" in result["script"]


@pytest.mark.asyncio
async def test_complete_video_generation(orchestrator):
    """Test complete video generation pipeline."""
    result = await orchestrator.generate_complete_video(video_type="long_form")
    assert "success" in result


@pytest.mark.asyncio
async def test_daily_generation(orchestrator):
    """Test daily content generation (1 Short + 1 Long-form)."""
    result = await orchestrator.generate_daily_content()
    assert "success" in result
    assert "short" in result
    assert "long_form" in result
