from django.contrib import admin
from .models import ExemplarySpeech

@admin.register(ExemplarySpeech)
class ExemplarySpeechAdmin(admin.ModelAdmin):
    list_display = ('speaker_name', 'title', 'category', 'date_delivered', 'has_transcript')
    search_fields = ('speaker_name', 'title', 'transcript')
    list_filter = ('category', 'date_delivered')
    readonly_fields = ('transcript',)

    def has_transcript(self, obj):
        return bool(obj.transcript)
    has_transcript.boolean = True
    has_transcript.short_description = 'Transcribed'
