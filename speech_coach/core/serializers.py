from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserSpeech, ExemplarySpeech, UserProfile
import json

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = '__all__'

class UserSpeechSerializer(serializers.ModelSerializer):
    analysis_summary = serializers.SerializerMethodField()
    ai_feedback = serializers.SerializerMethodField()
    duration_minutes = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = UserSpeech
        fields = [
            'id', 'user', 'title', 'audio_file', 'transcript',
            'date_delivered', 'occasion', 'category',
            'words_per_minute', 'clarity_score',
            'status', 'status_display', 'error_message',
            'created_at', 'updated_at',
            'analysis_summary', 'ai_feedback', 'duration_minutes'
        ]
        read_only_fields = [
            'user', 'transcript', 'words_per_minute',
            'clarity_score', 'status', 'error_message',
            'analysis_summary', 'ai_feedback'
        ]

    def get_analysis_summary(self, obj):
        if obj.status == 'completed':
            return obj.get_analysis_summary()
        return None

    def get_ai_feedback(self, obj):
        if obj.ai_feedback:
            try:
                return json.loads(obj.ai_feedback)
            except json.JSONDecodeError:
                return None
        return None

    def get_duration_minutes(self, obj):
        if obj.transcript and obj.words_per_minute:
            return len(obj.transcript.split()) / obj.words_per_minute
        return None

class ExemplarySpeechSerializer(serializers.ModelSerializer):
    duration_minutes = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = ExemplarySpeech
        fields = [
            'id', 'speaker_name', 'title', 'audio_file',
            'transcript', 'date_delivered', 'occasion',
            'category', 'status', 'status_display',
            'created_at', 'updated_at', 'duration_minutes'
        ]
        read_only_fields = ['transcript', 'status']

    def get_duration_minutes(self, obj):
        if obj.transcript:
            # Estimate duration based on average speaking rate
            return len(obj.transcript.split()) / 130  # Using average speaking rate
        return None

class SpeechAnalysisSerializer(serializers.Serializer):
    """Serializer for detailed speech analysis response"""
    metrics = serializers.DictField()
    similar_speeches = serializers.ListField(child=serializers.DictField())
    ai_feedback = serializers.DictField(required=False)
    status = serializers.CharField()

    class Meta:
        fields = ['metrics', 'similar_speeches', 'ai_feedback', 'status']
