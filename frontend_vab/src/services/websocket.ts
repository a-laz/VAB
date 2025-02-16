export class WebSocketService {
    private ws: WebSocket | null = null;
    private audioContext: AudioContext;
    private mediaRecorder: MediaRecorder | null = null;
    private onMessageCallback: ((event: MessageEvent) => void) | null = null;

    constructor() {
        this.audioContext = new AudioContext();
    }

    connect(speechId: string) {
        this.ws = new WebSocket(`ws://localhost:8000/ws/speeches/${speechId}/live/`);

        this.ws.onopen = () => {
            console.log('WebSocket Connected');
        };

        this.ws.onmessage = (event) => {
            if (this.onMessageCallback) {
                this.onMessageCallback(event);
            }
            this.handleAudioMessage(event);
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket Error:', error);
        };

        this.ws.onclose = () => {
            console.log('WebSocket Disconnected');
        };
    }

    setMessageCallback(callback: (event: MessageEvent) => void) {
        this.onMessageCallback = callback;
    }

    private async handleAudioMessage(event: MessageEvent) {
        try {
            const data = JSON.parse(event.data);

            if (data.type === 'response.audio.delta') {
                // Convert base64 audio to audio buffer and play
                const audioData = atob(data.delta);
                const arrayBuffer = new ArrayBuffer(audioData.length);
                const view = new Uint8Array(arrayBuffer);
                for (let i = 0; i < audioData.length; i++) {
                    view[i] = audioData.charCodeAt(i);
                }

                const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
                const source = this.audioContext.createBufferSource();
                source.buffer = audioBuffer;
                source.connect(this.audioContext.destination);
                source.start();
            }
        } catch (error) {
            console.error('Error handling audio message:', error);
        }
    }

    async startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(stream);

            this.mediaRecorder.ondataavailable = async (event) => {
                if (event.data.size > 0 && this.ws?.readyState === WebSocket.OPEN) {
                    const reader = new FileReader();
                    reader.onloadend = () => {
                        const base64Audio = (reader.result as string).split(',')[1];
                        this.ws?.send(JSON.stringify({
                            type: 'input_audio_buffer.append',
                            audio: base64Audio
                        }));
                    };
                    reader.readAsDataURL(event.data);
                }
            };

            this.mediaRecorder.start(100); // Capture in 100ms chunks
        } catch (error) {
            console.error('Error starting recording:', error);
        }
    }

    stopRecording() {
        if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
            this.mediaRecorder.stop();
            this.mediaRecorder.stream.getTracks().forEach(track => track.stop());

            // Send commit message to indicate end of audio input
            if (this.ws?.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({
                    type: 'input_audio_buffer.commit'
                }));
            }
        }
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }
}

export const wsService = new WebSocketService(); 