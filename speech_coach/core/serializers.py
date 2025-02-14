from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserSpeech, ExemplarySpeech, UserProfile

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
    class Meta:
        model = UserSpeech
        fields = '__all__'

class ExemplarySpeechSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExemplarySpeech
        fields = '__all__'
