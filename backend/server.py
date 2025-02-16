import os
import json
import asyncio
import websocket
import logging
from dotenv import load_dotenv
from websockets.server import serve

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_WS_URL = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17"

class OpenAIWebSocket:
    def __init__(self, client_ws):
        self.client_ws = client_ws
        self.ws = None
        self.headers = [
            f"Authorization: Bearer {OPENAI_API_KEY}",
            "OpenAI-Beta: realtime=v1"
        ]

    def on_message(self, ws, message):
        """Handle messages from OpenAI"""
        try:
            data = json.loads(message)
            logger.info(f"Received from OpenAI: {json.dumps(data, indent=2)}")
            
            # Forward text deltas to the client
            if data.get("type") == "response.text.delta":
                asyncio.run(self.client_ws.send(json.dumps({
                    "type": "text.data",
                    "text": {
                        "content": data.get("delta", "")
                    }
                })))
        except Exception as e:
            logger.error(f"Error handling OpenAI message: {e}")

    def on_error(self, ws, error):
        """Handle WebSocket errors"""
        logger.error(f"OpenAI WebSocket error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket closure"""
        logger.info("OpenAI WebSocket connection closed")

    def on_open(self, ws):
        """Handle WebSocket connection open"""
        logger.info("Connected to OpenAI")
        # Initialize the session with text modality
        init_event = {
            "type": "session.update",
            "session": {
                "modalities": ["text"],
                "instructions": "You are an AI interviewer. Conduct the interview professionally.",
                "temperature": 0.7,
                "max_response_output_tokens": 1000
            }
        }
        ws.send(json.dumps(init_event))

    def connect(self):
        """Establish connection to OpenAI"""
        self.ws = websocket.WebSocketApp(
            OPENAI_WS_URL,
            header=self.headers,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        return self.ws

    def send(self, message):
        """Send message to OpenAI"""
        if self.ws:
            # Convert client message to OpenAI format
            data = json.loads(message)
            if data.get("type") == "text.data":
                event = {
                    "type": "response.create",
                    "response": {
                        "modalities": ["text"],
                        "instructions": "You are an AI interviewer. Conduct the interview professionally."
                    }
                }
                self.ws.send(json.dumps(event))

async def handle_client(websocket):
    """Handle individual client connections"""
    try:
        # Create OpenAI WebSocket connection
        openai_ws = OpenAIWebSocket(websocket)
        ws = openai_ws.connect()
        
        # Run OpenAI WebSocket in a separate thread
        import threading
        ws_thread = threading.Thread(target=ws.run_forever)
        ws_thread.daemon = True
        ws_thread.start()

        # Handle messages from the client
        async for message in websocket:
            try:
                data = json.loads(message)
                logger.info(f"Received from client: {data}")
                openai_ws.send(message)
            except json.JSONDecodeError:
                logger.error("Invalid JSON received from client")
                
    except Exception as e:
        logger.error(f"Error in client handler: {e}")
    finally:
        if 'ws' in locals():
            ws.close()

async def main():
    """Start the WebSocket server"""
    async with serve(handle_client, "localhost", 8000):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main()) 