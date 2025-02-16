from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserSpeech, ExemplarySpeech, UserProfile, InterviewSession
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

class InterviewSessionSerializer(serializers.ModelSerializer):
    duration_minutes = serializers.ChoiceField(choices=[5, 15, 30])
    
    class Meta:
        model = InterviewSession
        fields = [
            'id',
            'user',
            'job_role',
            'interview_type',
            'duration_minutes',
            'resume_url',
            'linkedin_url',
            'current_question',
            'questions_asked',
            'answers_given',
            'clarity_score',
            'structure_score',
            'relevance_score',
            'confidence_score',
            'ai_feedback',
            'suggested_improvements',
            'status',
            'started_at',
            'completed_at',
            'next_session_scheduled',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'questions_asked',
            'answers_given',
            'clarity_score',
            'structure_score',
            'relevance_score',
            'confidence_score',
            'ai_feedback',
            'suggested_improvements',
            'status',
            'started_at',
            'completed_at',
            'created_at',
            'updated_at'
        ]

    def validate_interview_type(self, value):
        valid_types = ['behavioral', 'technical', 'case_study']
        if value not in valid_types:
            raise serializers.ValidationError(f"Interview type must be one of: {', '.join(valid_types)}")
        return value

    def validate_duration_minutes(self, value):
        if value not in [5, 15, 30]:
            raise serializers.ValidationError("Duration must be 5, 15, or 30 minutes")
        return value

    def create(self, validated_data):
        validated_data['status'] = 'pending'
        return super().create(validated_data)
