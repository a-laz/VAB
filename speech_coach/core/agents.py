from typing import List, Dict, Optional
from datetime import datetime, timedelta
import openai
import json
from django.conf import settings

class InterviewAgent:
    def __init__(self, job_role: str, interview_type: str, resume: Optional[str] = None, job_description: Optional[str] = None):
        if not job_role or not interview_type:
            raise ValueError("Job role and interview type must not be empty")
            
        if interview_type not in ['technical', 'behavioral', 'case_study']:
            raise ValueError("Invalid interview type")
        
        self.job_role = job_role
        self.interview_type = interview_type
        self.resume = resume
        self.job_description = job_description
        self.conversation_history = []
        self.current_question_index = 0
        self.session_start_time = None
        
    def get_system_prompt(self) -> str:
        base_prompt = """You are an experienced technical interviewer and coach. Your role is to:
        1. Conduct professional interviews
        2. Provide constructive feedback
        3. Suggest specific improvements
        4. Maintain a supportive tone
        5. Schedule follow-up sessions
        
        Current interview context:
        Role: {role}
        Type: {type}
        """.format(role=self.job_role, type=self.interview_type)
        
        if self.resume and self.job_description:
            base_prompt += f"\nResume: {self.resume}\nJob Description: {self.job_description}"
            
        return base_prompt

    async def start_conversation(self) -> str:
        """Initial greeting and interview type selection"""
        self.session_start_time = datetime.now()
        return "As an AI coach, I'm here to help you improve your speaking. Which type do you want to practice - mock interview, presentation, or daily chat?"

    async def handle_interview_setup(self, has_materials: bool) -> str:
        """Handle resume and job description request"""
        if not has_materials:
            return "Great choice! Let's get started. Can you share your resume and the job description? I'll act as your interviewer."
        return f"Thanks! Excited to run this mock interview for {self.job_role}. Let's begin—can you introduce yourself?"

    async def process_response(self, answer: str) -> Dict:
        """Process candidate's answer and generate feedback"""
        self.conversation_history.append({"role": "user", "content": answer})
        
        analysis_prompt = """Analyze the response and provide:
        {
            "score": <0-10>,
            "strengths": ["strength1", "strength2"],
            "improvements": ["improvement1", "improvement2"],
            "feedback": "encouraging feedback highlighting positives",
            "follow_up_question": "next question based on response"
        }"""
        
        self.conversation_history.append({"role": "user", "content": analysis_prompt})
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=self.conversation_history,
            temperature=0.7,
            response_format={ "type": "json_object" }
        )
        
        analysis = response.choices[0].message.content
        self.conversation_history.append({"role": "assistant", "content": analysis})
        
        return json.loads(analysis)

    def suggest_next_session(self) -> str:
        """Suggest next session time based on current session"""
        if not self.session_start_time:
            return "Would you like to schedule another practice session?"
            
        current_time = self.session_start_time
        tomorrow_same_time = current_time + timedelta(days=1)
        next_wednesday = current_time + timedelta(days=(2 - current_time.weekday() + 7) % 7)
        
        return f"Since we met today at {current_time.strftime('%I %p')}, do you want to practice again at the same time tomorrow? If not, let me know a time that works, like {next_wednesday.strftime('%I %p')} this Wednesday."

    def format_feedback(self, analysis: Dict) -> str:
        """Format feedback message"""
        return f"""Here's how you did: {analysis['score']} out of 10.
        Strengths: {', '.join(analysis['strengths'])}
        Areas to improve: {', '.join(analysis['improvements'])}
        
        {analysis['feedback']}"""

    def get_behavioral_questions(self) -> List[str]:
        return [
            "Tell me about a challenging project you worked on.",
            "Describe a situation where you had to deal with a difficult team member.",
            "Give an example of a time you had to meet a tight deadline.",
            # Add more questions...
        ]

    def get_technical_questions(self) -> List[str]:
        return [
            f"What technical skills are most important for a {self.job_role}?",
            "Describe your experience with relevant technologies.",
            "How do you stay updated with industry trends?",
            # Add more questions...
        ]
