from rest_framework import serializers
from .models import UserSpeech, ExemplarySpeech

class UserSpeechSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSpeech
        fields = '__all__'

class ExemplarySpeechSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExemplarySpeech
        fields = '__all__'
