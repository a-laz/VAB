from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from .models import UserSpeech, ExemplarySpeech, UserProfile
from .serializers import UserSpeechSerializer, ExemplarySpeechSerializer, UserProfileSerializer
from django.contrib.auth.models import User
import json

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
