"""Test workflow orchestrator."""

import pytest
from workflow import ContentOrchestrator


def test_orchestrator_init():
    """Test ContentOrchestrator initializes with all agents."""
    orchestrator = ContentOrchestrator()
    assert orchestrator.trend_research is not None
    assert orchestrator.topic_selection is not None
    assert orchestrator.research is not None
    assert orchestrator.scriptwriting is not None
    assert orchestrator.fact_checking is not None
    assert orchestrator.voice_generation is not None
    assert orchestrator.visual_generation is not None
    assert orchestrator.video_editing is not None
    assert orchestrator.thumbnail is not None
    assert orchestrator.seo is not None
    assert orchestrator.quality_control is not None
    assert orchestrator.youtube_upload is not None
    assert orchestrator.analytics is not None
    assert orchestrator.optimization is not None
