from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
import assemblyai as aai
from django.conf import settings
from threading import Thread
import os

# Create your models here.

class ExemplarySpeech(models.Model):
    speaker_name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    audio_file = models.FileField(upload_to='exemplary_speeches/')
    transcript = models.TextField(blank=True, null=True)
    date_delivered = models.DateField(null=True, blank=True)
    occasion = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=100, blank=True)
    # Vector field for embedding
    embedding = models.JSONField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.speaker_name} - {self.title}"

    def transcribe_audio(self):
        if self.audio_file and not self.transcript:
            try:
                # Initialize AssemblyAI client
                aai.settings.api_key = settings.ASSEMBLYAI_API_KEY
                
                # Create transcription object
                transcriber = aai.Transcriber()
                
                # Get the full file path
                file_path = os.path.join(settings.MEDIA_ROOT, self.audio_file.name)
                
                # Start transcription with local file
                transcript = transcriber.transcribe(file_path)
                
                if transcript.text:
                    self.transcript = transcript.text
                    self.save(update_fields=['transcript'])
                    print(f"Transcription completed for {self.title}")
                else:
                    print(f"No transcript generated for {self.title}")
                    
            except Exception as e:
                print(f"Error transcribing {self.title}: {str(e)}")

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        # Start transcription in background only for new objects
        if is_new and not self.transcript and 'update_fields' not in kwargs:
            Thread(target=self.transcribe_audio).start()

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

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    speaking_goals = models.TextField(blank=True)
    experience_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
        ],
        default='beginner'
    )
    total_speeches = models.IntegerField(default=0)
    average_clarity_score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

# Signal to automatically create/update UserProfile when User is created/updated
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.profile.save()
