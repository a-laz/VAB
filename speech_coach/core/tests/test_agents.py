import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import sys
import os
import json

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.agents import InterviewAgent

@pytest.fixture
def interview_agent():
    return InterviewAgent(
        job_role="Software Engineer",
        interview_type="technical"
    )

@pytest.mark.asyncio
async def test_interview_agent_initialization(interview_agent):
    """Test that the interview agent initializes correctly"""
    assert interview_agent.job_role == "Software Engineer"
    assert interview_agent.interview_type == "technical"
    assert len(interview_agent.conversation_history) == 0
    assert interview_agent.current_question_index == 0

@pytest.mark.asyncio
async def test_system_prompt_generation(interview_agent):
    """Test system prompt contains required information"""
    system_prompt = interview_agent.get_system_prompt()
    assert "Software Engineer" in system_prompt
    assert "technical interview" in system_prompt
    assert "guidelines" in system_prompt

@pytest.mark.asyncio
async def test_start_interview(interview_agent):
    """Test that the interview agent starts correctly"""
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="Tell me about your experience."))
    ]
    
    # Create an async context manager mock
    async def async_mock(*args, **kwargs):
        return mock_response
    
    with patch('openai.ChatCompletion.acreate', new=async_mock):
        first_question = await interview_agent.start_interview()
        assert "Tell me about your experience" in first_question
        assert len(interview_agent.conversation_history) == 3

@pytest.mark.asyncio
async def test_process_response(interview_agent):
    """Test processing of candidate responses"""
    mock_analysis = {
        "quality_score": 85,
        "strengths": ["Clear communication"],
        "improvements": ["More examples needed"],
        "follow_up_question": "Can you elaborate?"
    }
    
    async def async_mock(*args, **kwargs):
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps(mock_analysis)))
        ]
        return mock_response
    
    with patch('openai.ChatCompletion.acreate', new=async_mock):
        analysis = await interview_agent.process_response("I have 5 years of experience.")
        analysis_dict = json.loads(analysis)
        
        assert analysis_dict["quality_score"] == 85
        assert "Clear communication" in analysis_dict["strengths"]
        assert len(interview_agent.conversation_history) > 0

@pytest.mark.asyncio
async def test_behavioral_questions(interview_agent):
    """Test behavioral question generation"""
    questions = interview_agent.get_behavioral_questions()
    assert len(questions) > 0
    assert all(isinstance(q, str) for q in questions)
    assert any("challenging project" in q.lower() for q in questions)

@pytest.mark.asyncio
async def test_technical_questions(interview_agent):
    """Test technical question generation"""
    questions = interview_agent.get_technical_questions()
    assert len(questions) > 0
    assert all(isinstance(q, str) for q in questions)
    assert any("technical skills" in q.lower() for q in questions)

@pytest.mark.asyncio
async def test_conversation_history_maintenance(interview_agent):
    """Test that conversation history is maintained correctly"""
    mock_start = MagicMock()
    mock_start.choices = [
        MagicMock(message=MagicMock(content="First question"))
    ]
    
    async def async_mock_start(*args, **kwargs):
        return mock_start
        
    with patch('openai.ChatCompletion.acreate', new=async_mock_start):
        await interview_agent.start_interview()
        initial_history_length = len(interview_agent.conversation_history)
        
        mock_analysis = {
            "quality_score": 90,
            "strengths": ["Good"],
            "improvements": ["None"],
            "follow_up_question": "Next question"
        }
        
        async def async_mock_process(*args, **kwargs):
            mock_response = MagicMock()
            mock_response.choices = [
                MagicMock(message=MagicMock(content=json.dumps(mock_analysis)))
            ]
            return mock_response
            
        with patch('openai.ChatCompletion.acreate', new=async_mock_process):
            await interview_agent.process_response("Test answer")
            assert len(interview_agent.conversation_history) > initial_history_length

@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling for invalid inputs"""
    with pytest.raises(ValueError):
        InterviewAgent("", "")  # Empty strings should raise error
    
    with pytest.raises(ValueError):
        InterviewAgent("Software Engineer", "invalid_type")  # Invalid interview type 