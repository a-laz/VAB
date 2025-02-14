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
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('transcribing', 'Transcribing'),
        ('embedding', 'Generating Embedding'),
        ('analyzing', 'Analyzing Speech'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    audio_file = models.FileField(upload_to='user_speeches/')
    transcript = models.TextField(blank=True, null=True)
    date_delivered = models.DateField(auto_now_add=True)
    occasion = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=100, blank=True)
    embedding = models.JSONField(null=True, blank=True)
    
    # Speech Analysis Metrics
    words_per_minute = models.FloatField(null=True, blank=True)
    pause_duration = models.JSONField(null=True, blank=True)  # Store pause timestamps and durations
    volume_variation = models.JSONField(null=True, blank=True)  # Store volume levels over time
    filler_words = models.JSONField(null=True, blank=True)  # Store filler word counts and timestamps
    clarity_score = models.FloatField(null=True, blank=True)  # Overall clarity score
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    error_message = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def transcribe_and_analyze(self):
        if self.audio_file and not self.transcript:
            try:
                self.status = 'transcribing'
                self.save(update_fields=['status'])

                # Initialize AssemblyAI client
                aai.settings.api_key = settings.ASSEMBLYAI_API_KEY
                
                # Create transcription object with analysis features
                config = aai.TranscriptionConfig(
                    word_boost=['um', 'uh', 'like', 'you know'],
                    speech_threshold=0.2,
                    word_timestamps=True,
                    auto_highlights=True,
                    content_safety=False,
                    disfluencies=True,
                    sentiment_analysis=True,
                    auto_chapters=True
                )
                
                transcriber = aai.Transcriber()
                transcript = transcriber.transcribe(
                    os.path.join(settings.MEDIA_ROOT, self.audio_file.name),
                    config=config
                )
                
                if transcript.text:
                    self.status = 'analyzing'
                    self.save(update_fields=['status'])
                    
                    # Store transcript
                    self.transcript = transcript.text
                    
                    # Calculate words per minute
                    duration_minutes = transcript.audio_duration / 60
                    word_count = len(transcript.words)
                    self.words_per_minute = word_count / duration_minutes
                    
                    # Analyze pauses
                    self.pause_duration = self._analyze_pauses(transcript.words)
                    
                    # Count filler words
                    self.filler_words = self._count_filler_words(transcript.words)
                    
                    # Calculate clarity score based on confidence scores
                    self.clarity_score = self._calculate_clarity(transcript.words)
                    
                    self.status = 'embedding' if not self.embedding else 'completed'
                    self.save()
                    
                    print(f"Analysis completed for {self.title}")
                else:
                    self.status = 'failed'
                    self.error_message = "No transcript generated"
                    self.save(update_fields=['status', 'error_message'])
                    
            except Exception as e:
                self.status = 'failed'
                self.error_message = str(e)
                self.save(update_fields=['status', 'error_message'])
                print(f"Error analyzing {self.title}: {str(e)}")

    def _analyze_pauses(self, words):
        pauses = []
        for i in range(len(words) - 1):
            current_word_end = words[i]['end']
            next_word_start = words[i + 1]['start']
            pause_duration = next_word_start - current_word_end
            if pause_duration > 1.0:  # Consider pauses longer than 1 second
                pauses.append({
                    'timestamp': current_word_end,
                    'duration': pause_duration
                })
        return pauses

    def _count_filler_words(self, words):
        filler_words = {
            'um': [], 'uh': [], 'like': [], 'you know': []
        }
        
        for word in words:
            if word['text'].lower() in filler_words:
                filler_words[word['text'].lower()].append({
                    'timestamp': word['start'],
                    'confidence': word['confidence']
                })
        return filler_words

    def _calculate_clarity(self, words):
        confidence_scores = [word['confidence'] for word in words]
        return sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0

    def get_analysis_summary(self):
        """Return a summary of the speech analysis"""
        if self.status != 'completed':
            return {'status': self.status}
            
        return {
            'pacing': {
                'words_per_minute': self.words_per_minute,
                'target_range': '120-150 wpm',
                'assessment': self._assess_pacing()
            },
            'pauses': {
                'count': len(self.pause_duration) if self.pause_duration else 0,
                'long_pauses': len([p for p in (self.pause_duration or []) if p['duration'] > 2]),
                'suggestions': self._get_pause_suggestions()
            },
            'filler_words': {
                'total_count': sum(len(occurrences) for occurrences in (self.filler_words or {}).values()),
                'breakdown': self.filler_words,
                'suggestions': self._get_filler_word_suggestions()
            },
            'clarity': {
                'score': self.clarity_score * 100 if self.clarity_score else 0,
                'assessment': self._assess_clarity()
            }
        }

    def _assess_pacing(self):
        if not self.words_per_minute:
            return "No pacing data available"
        if self.words_per_minute < 120:
            return "Speech is slower than recommended. Try to increase your pace slightly."
        elif self.words_per_minute > 150:
            return "Speech is faster than recommended. Try to slow down for better clarity."
        return "Good pace! You're speaking at an ideal rate."

    def _get_pause_suggestions(self):
        if not self.pause_duration:
            return "No pause data available"
        suggestions = []
        if len(self.pause_duration) > 10:
            suggestions.append("Consider reducing the number of long pauses")
        if any(p['duration'] > 3 for p in self.pause_duration):
            suggestions.append("Some pauses are too long. Try to keep pauses under 2 seconds")
        return suggestions if suggestions else ["Good use of pauses!"]

    def _assess_clarity(self):
        if not self.clarity_score:
            return "No clarity data available"
        score = self.clarity_score * 100
        if score > 90:
            return "Excellent clarity and pronunciation!"
        elif score > 75:
            return "Good clarity. Focus on enunciating challenging words."
        return "Consider speaking more clearly and practicing pronunciation."

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
                Thread(target=self.transcribe_and_analyze).start()
            if not self.embedding:
                Thread(target=self.generate_audio_embedding).start()

    def find_similar_speeches(self, limit=5):
        """Find similar exemplary speeches based on embedding similarity"""
        if not self.embedding:
            return []
            
        similarities = []
        exemplary_speeches = ExemplarySpeech.objects.exclude(embedding__isnull=True)
        
        for speech in exemplary_speeches:
            similarity = ExemplarySpeech.cosine_similarity(
                self.embedding, 
                speech.embedding
            )
            similarities.append((speech, similarity))
        
        # Sort by similarity score
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:limit]

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
