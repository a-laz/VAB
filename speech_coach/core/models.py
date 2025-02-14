from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
import assemblyai as aai
from django.conf import settings
from threading import Thread
import os
import torch
import torchaudio
from transformers import Wav2Vec2Model, Wav2Vec2Processor
import numpy as np

# Create your models here.

class ExemplarySpeech(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('transcribing', 'Transcribing'),
        ('embedding', 'Generating Embedding'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    speaker_name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    audio_file = models.FileField(upload_to='exemplary_speeches/')
    transcript = models.TextField(blank=True, null=True)
    date_delivered = models.DateField(null=True, blank=True)
    occasion = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=100, blank=True)
    embedding = models.JSONField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    error_message = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.speaker_name} - {self.title}"

    def transcribe_audio(self):
        if self.audio_file and not self.transcript:
            try:
                self.status = 'transcribing'
                self.save(update_fields=['status'])

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
                    self.status = 'embedding' if not self.embedding else 'completed'
                    self.save(update_fields=['transcript', 'status'])
                    print(f"Transcription completed for {self.title}")
                else:
                    self.status = 'failed'
                    self.error_message = "No transcript generated"
                    self.save(update_fields=['status', 'error_message'])
                    print(f"No transcript generated for {self.title}")
                    
            except Exception as e:
                self.status = 'failed'
                self.error_message = str(e)
                self.save(update_fields=['status', 'error_message'])
                print(f"Error transcribing {self.title}: {str(e)}")

    def generate_audio_embedding(self):
        if self.audio_file and not self.embedding:
            try:
                if not self.transcript:
                    self.status = 'transcribing'
                else:
                    self.status = 'embedding'
                self.save(update_fields=['status'])

                # Load model and processor
                processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
                model = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base-960h")
                
                # Get audio file path
                file_path = os.path.join(settings.MEDIA_ROOT, self.audio_file.name)
                
                try:
                    # Try loading with torchaudio first
                    waveform, sample_rate = torchaudio.load(file_path)
                except:
                    # If that fails, use soundfile as fallback
                    import soundfile as sf
                    waveform, sample_rate = sf.read(file_path)
                    waveform = torch.FloatTensor(waveform)
                    if len(waveform.shape) == 1:
                        waveform = waveform.unsqueeze(0)
                    else:
                        waveform = waveform.transpose(0, 1)
                
                # Resample if necessary (wav2vec expects 16kHz)
                if sample_rate != 16000:
                    resampler = torchaudio.transforms.Resample(sample_rate, 16000)
                    waveform = resampler(waveform)
                
                # Convert to mono if stereo
                if waveform.shape[0] > 1:
                    waveform = torch.mean(waveform, dim=0, keepdim=True)
                
                # Process through wav2vec
                input_values = processor(waveform.squeeze().numpy(), 
                                      sampling_rate=16000, 
                                      return_tensors="pt").input_values
                
                with torch.no_grad():
                    outputs = model(input_values)
                    # Use mean pooling to get a single vector
                    embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
                
                # Store the embedding
                self.embedding = embedding.tolist()
                self.status = 'completed'
                self.save(update_fields=['embedding', 'status'])
                print(f"Generated embedding for {self.title}")
                
            except Exception as e:
                self.status = 'failed'
                self.error_message = str(e)
                self.save(update_fields=['status', 'error_message'])
                print(f"Error generating embedding for {self.title}: {str(e)}")

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        
        if is_new and 'update_fields' not in kwargs:
            # Start transcription and embedding generation in background
            if not self.transcript:
                Thread(target=self.transcribe_audio).start()
            if not self.embedding:
                Thread(target=self.generate_audio_embedding).start()
    
    @staticmethod
    def cosine_similarity(embedding1, embedding2):
        if not embedding1 or not embedding2:
            return 0
        
        # Convert to numpy arrays
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Calculate cosine similarity
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

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
