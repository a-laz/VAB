from django.shortcuts import render
from rest_framework import generics, permissions
from .models import UserSpeech, ExemplarySpeech, UserProfile
from .serializers import UserSpeechSerializer, ExemplarySpeechSerializer, UserProfileSerializer
from django.contrib.auth.models import User

# Create your views here.

class SpeechList(generics.ListCreateAPIView):
    queryset = UserSpeech.objects.all()
    serializer_class = UserSpeechSerializer

class SpeechDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserSpeech.objects.all()
    serializer_class = UserSpeechSerializer

class ExemplarySpeechList(generics.ListAPIView):
    queryset = ExemplarySpeech.objects.all()
    serializer_class = ExemplarySpeechSerializer

class UserProfileDetail(generics.RetrieveUpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile
