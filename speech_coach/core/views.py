from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from .models import UserSpeech, ExemplarySpeech, UserProfile, InterviewSession
from .serializers import UserSpeechSerializer, ExemplarySpeechSerializer, UserProfileSerializer, InterviewSessionSerializer
from django.contrib.auth.models import User
import json
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
from rest_framework import viewsets
from rest_framework.decorators import action

# Create your views here.

class UserSpeechList(generics.ListCreateAPIView):
    """List all user speeches or create a new speech"""
    serializer_class = UserSpeechSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserSpeech.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserSpeechDetail(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a user speech"""
    serializer_class = UserSpeechSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserSpeech.objects.filter(user=self.request.user)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def speech_analysis(request, speech_id):
    """Get detailed analysis for a specific speech"""
    speech = get_object_or_404(UserSpeech, id=speech_id, user=request.user)
    
    analysis = {
        'status': speech.status,
        'metrics': speech.get_analysis_summary() if speech.status == 'completed' else None,
        'ai_feedback': json.loads(speech.ai_feedback) if speech.ai_feedback else None,
        'similar_speeches': [
            {
                'id': s[0].id,
                'title': s[0].title,
                'speaker': s[0].speaker_name,
                'similarity_score': f"{s[1]*100:.1f}%",
                'transcript': s[0].transcript
            }
            for s in speech.find_similar_speeches()
        ] if speech.status == 'completed' else []
    }
    
    return Response(analysis)

class ExemplarySpeechList(generics.ListAPIView):
    """List exemplary speeches"""
    queryset = ExemplarySpeech.objects.all()
    serializer_class = ExemplarySpeechSerializer
    permission_classes = [permissions.IsAuthenticated]

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def speech_status(request, speech_id):
    """Get the current processing status of a speech"""
    speech = get_object_or_404(UserSpeech, id=speech_id, user=request.user)
    return Response({
        'status': speech.status,
        'error': speech.error_message if speech.status == 'failed' else None
    })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def retry_processing(request, speech_id):
    """Retry processing a failed speech"""
    speech = get_object_or_404(UserSpeech, id=speech_id, user=request.user)
    if speech.status == 'failed':
        speech.status = 'pending'
        speech.error_message = None
        speech.save()
        # Restart processing
        speech.transcribe_and_analyze()
        return Response({'status': 'Processing restarted'})
    return Response(
        {'error': 'Can only retry failed speeches'}, 
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_statistics(request):
    """Get user's speaking statistics"""
    user_speeches = UserSpeech.objects.filter(
        user=request.user, 
        status='completed'
    )
    
    stats = {
        'total_speeches': user_speeches.count(),
        'average_wpm': sum(s.words_per_minute or 0 for s in user_speeches) / user_speeches.count() if user_speeches else 0,
        'average_clarity': sum(s.clarity_score or 0 for s in user_speeches) / user_speeches.count() if user_speeches else 0,
        'total_duration': sum(len(s.transcript.split()) / (s.words_per_minute or 120) for s in user_speeches) if user_speeches else 0,
        'recent_speeches': UserSpeechSerializer(
            user_speeches.order_by('-created_at')[:5], 
            many=True
        ).data
    }
    
    return Response(stats)

class UserProfileDetail(generics.RetrieveUpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile

class LiveTranscriptionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.speech_id = self.scope['url_route']['kwargs']['speech_id']
        self.speech = await self.get_speech()
        
        if not self.speech:
            await self.close()
            return
            
        await self.accept()
        
        # Start transcription session
        self.transcriber = await self.start_transcription()
        
    async def disconnect(self, close_code):
        if hasattr(self, 'transcriber'):
            await self.transcriber.close()
    
    async def receive(self, text_data=None, bytes_data=None):
        """Handle incoming audio chunks"""
        if bytes_data:
            # Process audio chunk
            await self.transcriber.process_audio(bytes_data)
            
    async def transcription_result(self, result):
        """Handle transcription result"""
        await self.speech.handle_transcription_result(result)
        
        # Send result to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'transcription',
            'text': result.text,
            'is_final': result.is_final,
            'confidence': result.confidence,
            'words': result.words,
            'analysis': await self.speech.get_analysis_summary()
        }))

class InterviewSessionViewSet(viewsets.ModelViewSet):
    serializer_class = InterviewSessionSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        # For development, return all sessions
        return InterviewSession.objects.all()
    
    @action(detail=False, methods=['post'])
    def schedule(self, request):
        # For development, create a default user if none exists
        if not User.objects.filter(username='default_user').exists():
            default_user = User.objects.create_user(username='default_user', password='password123')
        else:
            default_user = User.objects.get(username='default_user')
            
        # Schedule new interview session
        session = InterviewSession.objects.create(
            user=default_user,  # Use default user for development
            job_role=request.data['job_role'],
            interview_type=request.data['interview_type'],
            duration_minutes=request.data['duration_minutes'],  # Changed from duration to duration_minutes
            next_session_scheduled=request.data.get('scheduled_time')  # Made optional
        )
        return Response(InterviewSessionSerializer(session).data)
    
    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        session = self.get_object()
        return Response({
            'scores': {
                'clarity': session.clarity_score,
                'structure': session.structure_score,
                'relevance': session.relevance_score,
                'confidence': session.confidence_score
            },
            'improvement': session.suggested_improvements,
            'next_session': session.next_session_scheduled
        })
