from django.contrib import admin
from .models import ExemplarySpeech

@admin.register(ExemplarySpeech)
class ExemplarySpeechAdmin(admin.ModelAdmin):
    list_display = ('speaker_name', 'title', 'category', 'date_delivered', 'status', 'has_transcript', 'has_embedding')
    search_fields = ('speaker_name', 'title', 'transcript')
    list_filter = ('category', 'date_delivered', 'status')
    readonly_fields = ('transcript', 'embedding', 'status', 'error_message')

    def has_transcript(self, obj):
        return bool(obj.transcript)
    has_transcript.boolean = True
    has_transcript.short_description = 'Transcribed'

    def has_embedding(self, obj):
        return bool(obj.embedding)
    has_embedding.boolean = True
    has_embedding.short_description = 'Embedded'
