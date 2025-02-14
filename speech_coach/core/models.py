from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class ExemplarySpeech(models.Model):
    speaker_name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    audio_file = models.FileField(upload_to='exemplary_speeches/')
    transcript = models.TextField(blank=True)
    date_delivered = models.DateField(null=True, blank=True)
    occasion = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=100, blank=True)
    # Vector field for embedding
    embedding = models.JSONField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.speaker_name} - {self.title}"

class UserSpeech(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    audio_file = models.FileField(upload_to='user_speeches/')
    transcript = models.TextField(blank=True)
    feedback = models.TextField(blank=True)
    # Vector field for embedding
    embedding = models.JSONField(null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    duration = models.DurationField(null=True, blank=True)
    
    # Metrics
    words_per_minute = models.FloatField(null=True, blank=True)
    filler_word_count = models.IntegerField(null=True, blank=True)
    clarity_score = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
