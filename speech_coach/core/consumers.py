from channels.generic.websocket import AsyncWebsocketConsumer
import json
import os
import aiohttp
from .agents import InterviewAgent

class OpenAIRealtimeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        
        # Initialize OpenAI WebSocket connection
        self.openai_ws = None
        await self.setup_openai_connection()
        
    async def setup_openai_connection(self):
        url = "wss://api.openai.com/v1/realtime"
        headers = {
            "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY')}",
            "OpenAI-Beta": "realtime=v1"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(url, headers=headers) as ws:
                self.openai_ws = ws
                
                # Send initial setup event
                setup_event = {
                    "type": "response.create",
                    "response": {
                        "modalities": ["text"],
                        "instructions": "You are an AI assistant helping with speech analysis."
                    }
                }
                await ws.send_str(json.dumps(setup_event))
                
                # Handle incoming messages
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        data = json.loads(msg.data)
                        # Forward parsed data to client
                        await self.send(text_data=json.dumps({
                            "type": "openai.response",
                            "data": data
                        }))
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        break

    async def disconnect(self, close_code):
        if self.openai_ws:
            await self.openai_ws.close()

    async def receive(self, text_data=None, bytes_data=None):
        if self.openai_ws and text_data:
            # Parse incoming message
            try:
                data = json.loads(text_data)
                # Forward to OpenAI with proper event structure
                event = {
                    "type": data.get("type", "message"),
                    "content": data.get("content", "")
                }
                await self.openai_ws.send_str(json.dumps(event))
            except json.JSONDecodeError:
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format"
                }))

class InterviewConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.session = await self.get_session()
        
        if not self.session:
            await self.close()
            return
            
        # Initialize interview agent
        self.agent = InterviewAgent(
            job_role=self.session.job_role,
            interview_type=self.session.interview_type
        )
        
        await self.accept()
        
        # Start conversation
        initial_message = await self.agent.start_conversation()
        await self.send(json.dumps({
            "type": "conversation.start",
            "message": initial_message
        }))

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        
        if data['type'] == 'interview.setup':
            response = await self.agent.handle_interview_setup(
                has_materials='materials' in data and data['materials']
            )
            await self.send(json.dumps({
                "type": "interview.setup",
                "message": response
            }))
            
        elif data['type'] == 'answer':
            # Process answer
            analysis = await self.agent.process_response(data['content'])
            
            # Send feedback
            await self.send(json.dumps({
                "type": "interview.feedback",
                "message": self.agent.format_feedback(analysis),
                "analysis": analysis
            }))
            
            # If it's the end of the interview, suggest next session
            if data.get('is_last', False):
                next_session = self.agent.suggest_next_session()
                await self.send(json.dumps({
                    "type": "interview.schedule",
                    "message": next_session
                }))

    async def update_session_scores(self, analysis):
        """Update session scores based on answer analysis"""
        self.session.answers_given.append({
            "question": self.agent.conversation_history[-4]["content"],
            "answer": self.agent.conversation_history[-3]["content"],
            "score": analysis["quality_score"]
        })
        
        # Update average scores
        scores = [answer["score"] for answer in self.session.answers_given]
        self.session.clarity_score = sum(scores) / len(scores)
        
        await self.session.asave()
